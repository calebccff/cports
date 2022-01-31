pkgname = "glib-networking"
pkgver = "2.70.1"
pkgrel = 0
build_style = "meson"
configure_args = [
    "-Dgnutls=enabled", "-Dopenssl=enabled", "-Dlibproxy=enabled",
    "-Dgnome_proxy=enabled"
]
hostmakedepends = ["meson", "pkgconf", "gettext-tiny"]
makedepends = [
    "openssl-devel", "gnutls-devel", "gsettings-desktop-schemas-devel",
    "libglib-devel", "libproxy-devel"
]
depends = ["gsettings-desktop-schemas"]
checkdepends = ["glib"]
pkgdesc = "Network extensions for glib"
maintainer = "q66 <q66@chimera-linux.org>"
license = "LGPL-2.1-or-later"
url = "https://gitlab.gnome.org/GNOME/glib-networking"
source = f"$(GNOME_SITE)/{pkgname}/{pkgver[:-2]}/{pkgname}-{pkgver}.tar.xz"
sha256 = "2a16bfc2d271ccd3266e3fb462bc8a4103c02e81bbb339aa92d6fb060592d7bc"

def post_install(self):
    self.rm(self.destdir / "usr/lib/systemd", recursive = True)

@subpackage("glib-networking-openssl")
def _gnutls(self):
    self.pkgdesc = f"{pkgdesc} (OpenSSL backend)"
    # autoinstall if openssl is installed
    self.install_if = [f"{pkgname}={pkgver}-r{pkgrel}", "openssl"]

    return ["usr/lib/gio/modules/libgioopenssl.so"]

@subpackage("glib-networking-gnutls")
def _gnutls(self):
    self.pkgdesc = f"{pkgdesc} (GnuTLS backend)"
    # autoinstall if gnutls is installed
    self.install_if = [f"{pkgname}={pkgver}-r{pkgrel}", "gnutls"]

    return ["usr/lib/gio/modules/libgiognutls.so"]
