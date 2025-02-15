pkgname = "htop"
pkgver = "3.2.2"
pkgrel = 0
build_style = "gnu_configure"
configure_args = ["--enable-unicode", "--enable-sensors"]
makedepends = ["ncurses-devel", "libsensors-devel"]
pkgdesc = "Interactive process viewer"
maintainer = "Jami Kettunen <jami.kettunen@protonmail.com>"
license = "GPL-2.0-only"
url = "https://htop.dev"
source = f"https://github.com/htop-dev/htop/releases/download/{pkgver}/htop-{pkgver}.tar.xz"
sha256 = "bac9e9ab7198256b8802d2e3b327a54804dc2a19b77a5f103645b11c12473dc8"

configure_gen = []
