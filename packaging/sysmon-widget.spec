%global appdir /opt/%{name}

Name:           sysmon-widget
Version:        %{?appversion}%{!?appversion:1.0.0}
Release:        1%{?dist}
Summary:        Conky-style desktop system monitor widget

License:        MIT
URL:            https://github.com/s4rt4/sysmon-widget
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

Requires:       python3
Requires:       python3-tkinter
Requires:       python3-psutil
Requires:       python3-requests
Requires:       python3-dbus
Requires:       python3-pillow
Requires:       python3-xlib
# Optional: playerctl is one of two MPRIS backends (dbus is the fallback);
# pystray only powers a system tray, which GNOME usually lacks (the in-widget
# gear menu is the primary control surface there).
Recommends:     playerctl
Recommends:     python3-pystray

%description
A Python/Tkinter desktop widget showing clock, weather, network throughput,
CPU/RAM/battery/temperature, storage, top processes and MPRIS music metadata.
Tuned for Fedora + GNOME (Wayland/XWayland): an in-widget gear menu provides
Settings, Autostart, Restart and Exit when no system tray is available.

%prep
%setup -q

%install
install -d %{buildroot}%{appdir}/panels %{buildroot}%{appdir}/utils
install -m 0644 main.py config.py widget.py README.md requirements.txt %{buildroot}%{appdir}/
install -m 0644 panels/*.py %{buildroot}%{appdir}/panels/
install -m 0644 utils/*.py %{buildroot}%{appdir}/utils/

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<'EOF'
#!/usr/bin/env sh
cd /opt/sysmon-widget || exit 1
exec /usr/bin/python3 /opt/sysmon-widget/main.py "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/%{name}

install -d %{buildroot}%{_datadir}/applications %{buildroot}%{_sysconfdir}/xdg/autostart
install -m 0644 packaging/sysmon-widget.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop
install -m 0644 packaging/sysmon-widget.desktop %{buildroot}%{_sysconfdir}/xdg/autostart/%{name}.desktop

%files
%license LICENSE
%doc README.md
%{appdir}
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_sysconfdir}/xdg/autostart/%{name}.desktop

%post
update-desktop-database -q %{_datadir}/applications &>/dev/null || true

%postun
update-desktop-database -q %{_datadir}/applications &>/dev/null || true

%changelog
* Sun Jun 07 2026 s4rt4 <surat.sarta@gmail.com> - 1.0.0-1
- First Fedora/GNOME release: GNOME (Wayland/XWayland) port, in-widget gear
  menu (Settings/Autostart/Restart/Exit), weather panel, and the
  music-playback / workspace-switch layout fix.
