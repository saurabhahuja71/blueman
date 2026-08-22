#!/usr/bin/env bash
# Build blueman (+ companion) RPMs inside an Oracle Linux container.
# Usage: build-rpms.sh <ol-major> [out-dir]
set -euxo pipefail

OL="${1:?usage: build-rpms.sh <ol-major> [out-dir]}"
OUT="${2:-dist}"

# workspace is owned by another uid inside CI containers
git config --global --add safe.directory '*' 2>/dev/null || true

PYCAIRO_VERSION="${PYCAIRO_VERSION:-1.23.0}"
PYGOBJECT_VERSION="${PYGOBJECT_VERSION:-3.44.1}"

CRB="ol${OL}_codeready_builder"
dnf install -y dnf-plugins-core curl git-core
dnf config-manager --set-enabled "${CRB}" \
  || dnf config-manager setopt "${CRB}.enabled=1"

COMMON_PKGS=(
  rpm-build make curl gcc gcc-c++ autoconf automake libtool meson ninja-build iproute
  gettext gettext-devel intltool desktop-file-utils pkgconf-pkg-config
  glib2-devel gtk3-devel gdk-pixbuf2-devel bluez-libs-devel gobject-introspection-devel
  libnotify-devel NetworkManager-libnm-devel polkit-devel systemd-devel cairo-devel libffi-devel
  python-srpm-macros systemd-rpm-macros adwaita-icon-theme
)

if [[ "$OL" == "10" ]]; then
  PY=/usr/bin/python3
  dnf install -y "${COMMON_PKGS[@]}" \
    python3-devel python3-Cython python3-gobject-devel python3-cairo-devel
else
  # OL8/OL9 stock PyGObject targets their default interpreter (3.6/3.9),
  # too old for this fork (needs >= 3.11); build against python3.11 and ship
  # companion pycairo/pygobject RPMs compiled for it.
  PY=/usr/bin/python3.11
  dnf install -y "${COMMON_PKGS[@]}" python3.11-devel python3.11-Cython
fi

mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# ---- Companion RPMs for OL8/OL9 (pycairo + pygobject for python3.11) ----
# Built and installed first so the tarball-generating configure below can
# satisfy its pygobject-3.0 pkg-config check.
if [[ "$OL" != "10" ]]; then
  curl -fsSL -o ~/rpmbuild/SOURCES/pycairo-"${PYCAIRO_VERSION}".tar.gz \
    "https://files.pythonhosted.org/packages/source/p/pycairo/pycairo-${PYCAIRO_VERSION}.tar.gz"
  sed -e "s/^Version:.*/Version:        ${PYCAIRO_VERSION}/" \
    packaging/python311-pycairo.spec > ~/rpmbuild/SPECS/python311-pycairo.spec
  rpmbuild -ba ~/rpmbuild/SPECS/python311-pycairo.spec
  dnf install -y ~/rpmbuild/RPMS/x86_64/python311-pycairo-*.rpm

  curl -fsSL -o ~/rpmbuild/SOURCES/pygobject-"${PYGOBJECT_VERSION}".tar.xz \
    "https://download.gnome.org/sources/pygobject/${PYGOBJECT_VERSION%.*}/pygobject-${PYGOBJECT_VERSION}.tar.xz"
  sed -e "s/^Version:.*/Version:        ${PYGOBJECT_VERSION}/" \
    packaging/python311-pygobject.spec > ~/rpmbuild/SPECS/python311-pygobject.spec
  rpmbuild -ba ~/rpmbuild/SPECS/python311-pygobject.spec
  dnf install -y ~/rpmbuild/RPMS/x86_64/python311-pygobject-*.rpm
fi

# ---- Generate source tarball from this checkout ----
# OL8/OL9 ship automake < 1.16.3; the floor is not a hard feature requirement.
sed -i 's/^AM_INIT_AUTOMAKE(\[1\.16\.3/AM_INIT_AUTOMAKE([1.16/' configure.ac
export NOCONFIGURE=1
./autogen.sh
PYTHON="$PY" CYTHONEXEC="$PY -m cython" ./configure --disable-schemas-compile
make dist-gzip

VER=$(sed -n 's/^AC_INIT(\[blueman\], \[\([0-9][0-9.]*\)\].*/\1/p' configure.ac)
REL="1.$(date +%Y%m%d)git$(git rev-parse --short HEAD)"
[[ -n "$VER" ]] || { echo "cannot determine version" >&2; exit 1; }
cp "blueman-${VER}.tar.gz" ~/rpmbuild/SOURCES/

# ---- blueman RPM ----
sed -e "s/^Version:.*/Version:        ${VER}/" \
    -e "s/^Release:.*/Release:        ${REL}%{?dist}/" \
    packaging/blueman.spec > ~/rpmbuild/SPECS/blueman.spec
rpmbuild -ba ~/rpmbuild/SPECS/blueman.spec

# ---- Stage artifacts ----
rm -rf "${OUT}"
mkdir -p "${OUT}/el${OL}/x86_64" "${OUT}/srpm"
cp ~/rpmbuild/RPMS/x86_64/*.rpm "${OUT}/el${OL}/x86_64/"
find "${OUT}/el${OL}/x86_64" \( -name '*-debuginfo-*.rpm' -o -name '*-debugsource-*.rpm' \) -delete
cp ~/rpmbuild/SRPMS/*.rpm "${OUT}/srpm/"
echo "Done: ${OUT}/el${OL}/x86_64:"
ls -1 "${OUT}/el${OL}/x86_64/"
