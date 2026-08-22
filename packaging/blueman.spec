Name:           blueman
Version:        2.4.3
Release:        1%{?dist}
Summary:        GTK+ Bluetooth Manager

License:        GPLv3+
URL:            https://github.com/saurabhahuja71/blueman
Source0:        %{name}-%{version}.tar.gz

# Interpreter selection.
# OL8/OL9 ship PyGObject bindings only for their default interpreter (3.6/3.9),
# which is too old for this fork (requires >= 3.11). We build against
# python3.11 and depend on companion RPMs built alongside (see CI).
%if 0%{?el8}%{?el9}
%global blupyinterp /usr/bin/python3.11
%global blupysite %{_prefix}/lib/python3.11/site-packages
%global blupysitearch %{_prefix}/lib64/python3.11/site-packages
%global blupygi python311-pygobject
%else
%global blupyinterp /usr/bin/python3
%global blupysite %{python3_sitelib}
%global blupysitearch %{python3_sitearch}
%global blupygi python3-gobject
%endif

BuildRequires:  gcc gcc-c++ make autoconf automake gettext-devel intltool desktop-file-utils pkgconf-pkg-config
BuildRequires:  glib2-devel gtk3-devel gdk-pixbuf2-devel bluez-libs-devel gobject-introspection-devel libnotify-devel
BuildRequires:  NetworkManager-libnm-devel polkit-devel systemd-devel cairo-devel
%if "%{blupyinterp}" == "/usr/bin/python3.11"
BuildRequires:  python3.11-devel python3.11-Cython
Requires:       %{blupygi} >= 3.27.2
%else
BuildRequires:  python3-devel python3-Cython python3-gobject-devel python3-cairo-devel
Requires:       %{blupygi} >= 3.27.2 python3-cairo
%endif

Requires:       bluez bluez-obexd dbus dconf iproute adwaita-icon-theme
# GObject-introspection typelibs are dlopened at runtime and thus not picked up
# by automatic dependency generation; require their providers explicitly
Requires:       gtk3 gdk-pixbuf2 pango NetworkManager-libnm libnotify gobject-introspection
Recommends:     pulseaudio-module-bluetooth
Recommends:     notification-daemon

%description
Blueman is a GTK+ Bluetooth Manager for Linux.

%prep
%autosetup

%build
export PYTHON=%{blupyinterp}
export CYTHONEXEC="%{blupyinterp} -m cython"
%configure \
    --disable-static \
    --disable-schemas-compile \
    --disable-runtime-deps-check
%make_build

%install
%make_install
rm -f %{buildroot}%{_datadir}/doc/blueman/COPYING || :
rm -rf %{buildroot}%{_sharedstatedir}/blueman || :
find %{buildroot} -name '*.la' -delete
rm -rf %{buildroot}%{_datadir}/doc/blueman
find %{buildroot} -name '__pycache__' -type d -exec rm -rf {} +
find %{buildroot} -name '*.pyc' -delete
find %{buildroot} -name '*.pyo' -delete
rm -f %{buildroot}%{_datadir}/Thunar/sendto/thunar-sendto-blueman.desktop || :

%files
%license COPYING
%doc CHANGELOG.md README.md FAQ
%{_bindir}/*
%{blupysite}/blueman/
%{blupysitearch}/*.so
%{_libexecdir}/blueman-*
%{_sysconfdir}/xdg/autostart/blueman.desktop
%{_datadir}/applications/blueman-*.desktop
%{_datadir}/icons/hicolor/*/*/*
%{_datadir}/blueman/
%{_datadir}/locale/*/LC_MESSAGES/blueman.mo
%{_datadir}/dbus-1/services/org.blueman.*.service
%{_datadir}/dbus-1/system.d/org.blueman.*.conf
%{_datadir}/dbus-1/system-services/org.blueman.*.service
%{_datadir}/glib-2.0/schemas/org.blueman*.gschema.xml
%{_datadir}/polkit-1/actions/org.blueman.policy
%{_datadir}/polkit-1/rules.d/*.rules
%{_mandir}/man1/*
%{_unitdir}/blueman-*.service
%{_userunitdir}/blueman-*.service

%post
%systemd_post blueman-mechanism.service
%systemd_user_post blueman-applet.service

%postun
%systemd_postun_with_restart blueman-mechanism.service

%preun
%systemd_preun blueman-mechanism.service
%systemd_user_preun blueman-applet.service

%changelog
* Sat Aug 22 2026 Saurabh Ahuja <saurabhahuja71@users.noreply.github.com>
- Built for Oracle Linux from this fork's source tree
