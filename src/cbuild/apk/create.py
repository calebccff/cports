import os
import io
import gzip
import stat
import tarfile
import hashlib
import pathlib
import tempfile
import subprocess
from datetime import datetime

from . import util, sign

# emulate `du -ks` * 1024, which is what alpine uses for size
def _du_k(fl):
    hls = {}
    ret = 0
    for f in fl:
        st = f.lstat()
        if stat.S_ISDIR(st.st_mode) or stat.S_ISLNK(st.st_mode):
            ret += int(st.st_blocks / 2)
        elif not st.st_ino in hls:
            hls[st.st_ino] = True
            ret += int(st.st_blocks / 2)
    return ret * 1024

def _hash_file(fp, md):
    while True:
        chunk = fp.read(16 * 1024)
        if not chunk:
            break
        md.update(chunk)
    return md.hexdigest()

_scriptlets = {
    ".pre-install": True,
    ".pre-upgrade": True,
    ".pre-deinstall": True,
    ".post-install": True,
    ".post-upgrade": True,
    ".post-deinstall": True,
    ".trigger": True,
}

def create(
    pkgname, pkgver, arch, epoch, destdir, tmpdir, outfile, privkey, metadata
):
    tmpdir = pathlib.Path(tmpdir)
    dt = datetime.utcfromtimestamp(epoch)

    # collect file list
    destdir = pathlib.Path(destdir)
    flist = [destdir]
    for fl in pathlib.Path(destdir).iterdir():
        # ignore metadata
        if fl.is_file():
            continue
        flist.append(fl)
        if not fl.is_symlink():
            flist += fl.rglob("*")
    # sort it
    flist.sort()

    ctrl = b"# Generated by cbuild\n"
    ctrl += b"# " + dt.isoformat(" ").encode() + b"\n"

    def add_field(fn, fv):
        if not fv:
            return
        nonlocal ctrl
        ctrl += fn.encode() + b" = " + fv.encode() + b"\n"

    def meta_field(fn):
        if fn in metadata:
            add_field(fn, str(metadata[fn]))
            return True
        return False

    # add core fields

    add_field("pkgname", pkgname)
    add_field("pkgver", pkgver)

    meta_field("pkgdesc")
    meta_field("url")

    add_field("builddate", str(int(epoch)))

    meta_field("packager")
    meta_field("maintainer")

    psz = _du_k(flist)
    # prevent packages with empty files from being considered virtual
    if psz == 0 and len(flist) > 0:
        psz = 1

    add_field("size", str(psz))
    add_field("arch", arch)

    if not meta_field("origin"):
        add_field("origin", pkgname)

    meta_field("commit")
    meta_field("license")

    if "replaces" in metadata:
        for r in metadata["replaces"]:
            add_field("replaces", r)

    if "depends" in metadata:
        for p in metadata["depends"]:
            add_field("depend", p)

    if "shlib_requires" in metadata:
        for shl in metadata["shlib_requires"]:
            add_field("depend", "so:" + shl)

    if "pc_requires" in metadata:
        for pc in metadata["pc_requires"]:
            add_field("depend", "pc:" + pc)

    if "provides" in metadata:
        for p in metadata["provides"]:
            add_field("provides", p)

    meta_field("provider_priority")

    if "shlib_provides" in metadata:
        for soname, sover in metadata["shlib_provides"]:
            add_field("provides", "so:" + soname + "=" + sover)

    if "cmd_provides" in metadata:
        for cmd in metadata["cmd_provides"]:
            add_field("provides", "cmd:" + cmd)

    if "pc_provides" in metadata:
        for pc in metadata["pc_provides"]:
            add_field("provides", "pc:" + pc)

    if "install_if" in metadata and len(metadata["install_if"]) > 0:
        add_field("install_if", " ".join(metadata["install_if"]))

    if "triggers" in metadata:
        add_field("triggers", " ".join(metadata["triggers"]))

    if "file_modes" in metadata:
        fmodes = metadata["file_modes"]
    else:
        fmodes = {}

    # all archive files need some special attributes
    def ctrl_filter(tinfo):
        tinfo.mtime = int(epoch)
        if tinfo.name in fmodes:
            uname, gname, fmode = fmodes[tinfo.name]
            if uname:
                col = uname.find(":")
                tinfo.uname = uname[:col]
                tinfo.uid = int(uname[col + 1:])
            else:
                tinfo.uname = "root"
                tinfo.uid = 0
            if gname:
                col = gname.find(":")
                tinfo.gname = gname[:col]
                tinfo.gid = int(gname[col + 1:])
            else:
                tinfo.gname = "root"
                tinfo.gid = 0
        else:
            tinfo.uname = "root"
            tinfo.gname = "root"
            tinfo.uid = 0
            tinfo.gid = 0
        tinfo.pax_headers["ctime"] = "0"
        tinfo.pax_headers["atime"] = "0"
        return tinfo

    def hook_filter(tinfo):
        tinfo = ctrl_filter(tinfo)
        tinfo.mode = 0o755
        return tinfo

    # data filter also has checksums
    def data_filter(tinfo):
        tinfo = ctrl_filter(tinfo)

        if tinfo.issym():
            cksum = hashlib.sha1(tinfo.linkname.encode()).hexdigest()
        elif tinfo.isfile():
            with open(destdir / tinfo.name, "rb") as rf:
                cksum = _hash_file(rf, hashlib.sha1())
        else:
            cksum = None

        if cksum:
            tinfo.pax_headers["APK-TOOLS.checksum.SHA1"] = cksum

        return tinfo

    # data archive file
    dtarf = tempfile.TemporaryFile(dir = tmpdir)

    # first data, since we gotta checksum it for the pkginfo
    with tarfile.open(None, "w:gz", fileobj = dtarf) as dtar:
        for f in flist:
            rf = f.relative_to(destdir)
            # skip the root
            if len(rf.name) == 0:
                continue
            # add the file
            dtar.add(f, str(rf), recursive = False, filter = data_filter)

    # go back to the beginning after writing it
    dtarf.seek(0)

    # ended with sha256 of contents archive
    add_field("datahash", _hash_file(dtarf, hashlib.sha256()))

    # we'll need to read it one more time for the concat
    dtarf.seek(0)

    # now control, we need an uncompressed tar archive here for now
    ctario = io.BytesIO()

    with tarfile.open(None, "w", fileobj = ctario) as ctar:
        cinfo = ctrl_filter(tarfile.TarInfo(".PKGINFO"))
        cinfo.size = len(ctrl)
        with io.BytesIO(ctrl) as cstream:
            ctar.addfile(cinfo, cstream)
        sclist = []
        scpath = tmpdir / "scriptlets"
        for f in scpath.glob(f"{pkgname}.*"):
            if f.is_file() and f.suffix in _scriptlets:
                sclist.append(f.suffix)
        sclist.sort()
        for f in sclist:
            ctar.add(scpath / f"{pkgname}{f}", f, filter = hook_filter)

    # concat together
    with open(outfile, "wb") as ffile:
        # compressed, stripped control data
        compctl = gzip.compress(
            util.strip_tar_endhdr(ctario.getvalue()), mtime = int(epoch)
        )
        # if given a key, sign control data and write signature first
        if privkey:
            ffile.write(sign.sign(privkey, compctl, epoch))
        # then the control data
        ffile.write(compctl)
        # we don't need the control stream anymore
        ctario.close()
        # write the data and buffer it because it's potentially huge
        while True:
            buf = dtarf.read(16 * 1024)
            if not buf:
                break
            ffile.write(buf)

    # ditch the temporary data archive
    dtarf.close()
