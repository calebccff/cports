pkgname = "gnome-shell"
pkgver = "45.3"
pkgrel = 0
build_style = "meson"
configure_args = [
    "-Ddefault_library=shared",
    "-Dsystemd=false",
    "-Dtests=false",
]
make_check_wrapper = ["weston-headless-run"]
hostmakedepends = [
    "asciidoc",
    "gettext",
    "gjs-devel",
    "glib-devel",
    "gobject-introspection",
    "meson",
    "perl",
    "pkgconf",
    "sassc",
    "xsltproc",
]
makedepends = [
    "at-spi2-core-devel",
    "evolution-data-server-devel",
    "gcr-devel",
    "gjs-devel",
    "gnome-autoar-devel",
    "gnome-bluetooth-devel",
    "gnome-control-center-devel",
    "gnome-desktop-devel",
    "gsettings-desktop-schemas-devel",
    "gstreamer-devel",
    "gtk4-devel",
    "ibus-devel",
    "libpulse-devel",
    "libxml2-devel",
    "mutter-devel",
    "mutter-devel",
    "networkmanager-devel",
    "pipewire-devel",
    "polkit-devel",
    "startup-notification-devel",
]
depends = [
    "cmd:unzip!unzip",
    "gnome-control-center",
    "gsettings-desktop-schemas",
    "upower",
]
checkdepends = ["weston"]
pkgdesc = "Core user interface for GNOME"
maintainer = "q66 <q66@chimera-linux.org>"
license = "GPL-2.0-or-later"
url = "https://wiki.gnome.org/Projects/GnomeShell"
source = f"$(GNOME_SITE)/{pkgname}/{pkgver[:-2]}/{pkgname}-{pkgver}.tar.xz"
sha256 = "3a19724720d8274dc6bced68e0dd5fc7668a04cd79978cbbb8223474ccdda9ab"
# tests need libmutter-test
options = ["!check"]
