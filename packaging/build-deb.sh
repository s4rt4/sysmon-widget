#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-0.1.0}"
PKG="sysmon-widget"
BUILD_DIR="$ROOT_DIR/build-deb/${PKG}_${VERSION}_all"
DIST_DIR="$ROOT_DIR/dist"

rm -rf "$BUILD_DIR"
mkdir -p \
  "$BUILD_DIR/DEBIAN" \
  "$BUILD_DIR/opt/sysmon-widget/panels" \
  "$BUILD_DIR/opt/sysmon-widget/utils" \
  "$BUILD_DIR/usr/bin" \
  "$BUILD_DIR/usr/share/applications" \
  "$BUILD_DIR/etc/xdg/autostart" \
  "$DIST_DIR"

cp "$ROOT_DIR"/main.py "$ROOT_DIR"/config.py "$ROOT_DIR"/widget.py "$ROOT_DIR"/README.md "$ROOT_DIR"/requirements.txt "$BUILD_DIR/opt/sysmon-widget/"
cp "$ROOT_DIR"/panels/*.py "$BUILD_DIR/opt/sysmon-widget/panels/"
cp "$ROOT_DIR"/utils/*.py "$BUILD_DIR/opt/sysmon-widget/utils/"

# Same .desktop is used both as launcher entry and as system-wide autostart.
cp "$ROOT_DIR"/packaging/sysmon-widget.desktop "$BUILD_DIR/usr/share/applications/sysmon-widget.desktop"
cp "$ROOT_DIR"/packaging/sysmon-widget.desktop "$BUILD_DIR/etc/xdg/autostart/sysmon-widget.desktop"

cat > "$BUILD_DIR/DEBIAN/control" <<EOF
Package: $PKG
Version: $VERSION
Section: x11
Priority: optional
Architecture: all
Depends: python3, python3-tk, python3-psutil, python3-requests, python3-dbus, python3-pil, python3-xlib, python3-pystray, playerctl
Recommends: gir1.2-ayatanaappindicator3-0.1
Maintainer: s4rt4 <vinvan83@gmail.com>
Description: Desktop system monitor widget with tray
 A Python and Tkinter desktop widget showing clock, weather,
 network, system stats, storage, and music metadata. Runs with
 a system tray icon (Show/Hide, Settings, Autostart, Restart, Exit).
 The widget window stays out of the taskbar and pager.
EOF

cat > "$BUILD_DIR/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
chmod 0755 /usr/bin/sysmon-widget
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
exit 0
EOF

cat > "$BUILD_DIR/DEBIAN/postrm" <<'EOF'
#!/bin/sh
set -e
if [ "$1" = "purge" ]; then
    rm -f /etc/xdg/autostart/sysmon-widget.desktop
fi
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
exit 0
EOF

cat > "$BUILD_DIR/usr/bin/sysmon-widget" <<'EOF'
#!/usr/bin/env sh
cd /opt/sysmon-widget || exit 1
exec /usr/bin/python3 /opt/sysmon-widget/main.py "$@"
EOF

chmod 0755 "$BUILD_DIR/DEBIAN/postinst" "$BUILD_DIR/DEBIAN/postrm" "$BUILD_DIR/usr/bin/sysmon-widget"
dpkg-deb --root-owner-group --build "$BUILD_DIR" "$DIST_DIR/${PKG}_${VERSION}_all.deb"
echo "Built: $DIST_DIR/${PKG}_${VERSION}_all.deb"
