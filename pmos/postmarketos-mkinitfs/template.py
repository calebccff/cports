pkgname = "postmarketos-mkinitfs"
pkgver = "2.2.2"
pkgrel = 0
build_wrksrc = f"{pkgname}-{pkgver}"
build_style = "makefile"
make_build_args = [
    "CGO_ENABLED=0",
    # Otherwise these get passed to go
    "LDFLAGS=",
    "BINDIR=/usr/bin",
]
hostmakedepends = ["go", "scdoc"]
pkgdesc = "Tool to generate initramfs images for postmarketOS"
maintainer = "Caleb Connolly <caleb@connolly.tech>"
license = "GPL-2.0-or-later"
url = "https://gitlab.com/postmarketOS/postmarketos-mkinitfs"
source = [
    f"https://gitlab.com/postmarketOS/postmarketos-mkinitfs/-/archive/{pkgver}/postmarketos-mkinitfs-{pkgver}.tar.gz",
    f"https://gitlab.com/api/v4/projects/postmarketOS%2Fpostmarketos-mkinitfs/packages/generic/mkinitfs-vendor-{pkgver}/{pkgver}/mkinitfs-vendor-{pkgver}.tar.gz",
]
sha256 = [
    "84a58cdad5df3f6d3dee688ac787d1445b7c3a19860d1b68d0881cb705d7d5ef",
    "07568f6bfe158f5f8cf55e0ab57679f8af8b322e17fe24344410d6605d496c76",
]
options = ["!debug"]

def do_prepare(self):
    self.do("ln", "-s", "../vendor", f"{build_wrksrc}/vendor")

def do_build(self):
    tool_args = [
        "PREFIX=/usr",
    ]

    self.make.build(tool_args)

def do_install(self):
    self.install_bin("mkinitfs")
    self.install_man("mkinitfs.1")
    self.install_license("LICENSE")

def do_check(self):
    self.do("go", "test", "./...")
