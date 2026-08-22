Name:           python311-pycairo
Version:        1.23.0
Release:        1%{?dist}
Summary:        Python 3.11 bindings for the cairo graphics library

License:        LGPLv2 or MPLv1.1
URL:            https://github.com/pygobject/pycairo
Source0:        pycairo-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  cairo-devel
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  python3.11-devel

Requires:       python3.11

%description
Python 3.11 bindings for the cairo graphics library, built for Oracle Linux
releases whose default interpreter is older than the one required by blueman.

%package devel
Summary: Development files for python311-pycairo
Requires: %{name} = %{version}-%{release}

%description devel
Header and pkg-config file for building software against python311-pycairo.

%prep
%autosetup -n pycairo-%{version}

%build
meson setup _build --prefix=%{_prefix} -Dpython=/usr/bin/python3.11 -Dtests=false
ninja -C _build

%install
DESTDIR=%{buildroot} ninja -C _build install
find %{buildroot} -name '__pycache__' -type d -exec rm -rf {} +

%files
%license COPYING
%doc NEWS README.rst
%{_prefix}/lib*/python3.11/site-packages/cairo/
%{_prefix}/lib*/python3.11/site-packages/pycairo-*.egg-info

# kept in -devel (not the main package) so the main package never collides
# with the distro's python3-cairo-devel on machines where both are installed
%files devel
%{_includedir}/pycairo/
%{_libdir}/pkgconfig/py3cairo.pc
