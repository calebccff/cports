pkgname = "python-openssl"
pkgver = "23.3.0"
pkgrel = 1
build_style = "python_pep517"
hostmakedepends = [
    "python-build",
    "python-installer",
    "python-setuptools",
    "python-wheel",
]
depends = ["python-cryptography"]
checkdepends = [
    "python-flaky",
    "python-pretend",
    "python-pytest",
] + depends
pkgdesc = "Python interface to OpenSSL"
maintainer = "q66 <q66@chimera-linux.org>"
license = "Apache-2.0"
url = "https://pyopenssl.org"
source = f"$(PYPI_SITE)/p/pyOpenSSL/pyOpenSSL-{pkgver}.tar.gz"
sha256 = "6b2cba5cc46e822750ec3e5a81ee12819850b11303630d575e98108a079c2b12"
