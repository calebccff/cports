pkgname = "tty-copy"
pkgver = "0.2.2"
pkgrel = 0
build_style = "makefile"
make_cmd = "gmake"
# TODO: asciidoctor for manpage
make_build_target = "build-exec"
make_install_target = "install-exec"
hostmakedepends = ["gmake"]
pkgdesc = "Copy content to system clipboard using OSC52"
maintainer = "psykose <alice@ayaya.dev>"
license = "MIT"
url = "https://github.com/jirutka/tty-copy"
source = f"{url}/archive/refs/tags/v{pkgver}.tar.gz"
sha256 = "5dad7c9eeb1f13747f989e38c4165edd367e7c6c348545b28ac8c1fb50cf4716"
hardening = ["vis", "cfi"]
# no tests
options = ["!check"]


def post_install(self):
    self.install_license("LICENSE")
