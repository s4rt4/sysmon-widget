#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-1.0.0}"
PKG="sysmon-widget"
TOPDIR="$ROOT_DIR/build-rpm"
DIST_DIR="$ROOT_DIR/dist"

rm -rf "$TOPDIR"
mkdir -p "$TOPDIR"/{BUILD,RPMS,SOURCES,SPECS,SRPMS} "$DIST_DIR"

# Stage sources into a versioned dir, then tar for Source0 (%setup expects it).
STAGE="$TOPDIR/${PKG}-${VERSION}"
mkdir -p "$STAGE/panels" "$STAGE/utils" "$STAGE/packaging"
cp "$ROOT_DIR"/main.py "$ROOT_DIR"/config.py "$ROOT_DIR"/widget.py \
   "$ROOT_DIR"/README.md "$ROOT_DIR"/requirements.txt "$ROOT_DIR"/LICENSE "$STAGE/"
cp "$ROOT_DIR"/panels/*.py "$STAGE/panels/"
cp "$ROOT_DIR"/utils/*.py "$STAGE/utils/"
cp "$ROOT_DIR"/packaging/sysmon-widget.desktop "$STAGE/packaging/"
cp "$ROOT_DIR"/packaging/sysmon-widget.svg "$STAGE/packaging/"

tar -C "$TOPDIR" -czf "$TOPDIR/SOURCES/${PKG}-${VERSION}.tar.gz" "${PKG}-${VERSION}"

rpmbuild \
  --define "_topdir $TOPDIR" \
  --define "appversion $VERSION" \
  -bb "$ROOT_DIR/packaging/${PKG}.spec"

RPM_PATH="$(find "$TOPDIR/RPMS" -name '*.rpm' | head -1)"
cp "$RPM_PATH" "$DIST_DIR/"
echo "Built: $DIST_DIR/$(basename "$RPM_PATH")"
