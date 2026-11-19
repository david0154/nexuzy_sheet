#!/usr/bin/env bash
# Copyright (c) 2026 Nexuzy Lab
# Nexuzy Sheet - builds a Debian/Ubuntu .deb package from the PyInstaller bundle.
#
# Usage:  ./installers/linux/build_deb.sh [dist/nexuzy-sheet] [output dir]
# --------------------------------------------------------------------

set -euo pipefail

SOURCE_DIR="${1:-dist/nexuzy-sheet}"
OUT_DIR="${2:-dist/installers}"
VERSION="$(python3 -c 'from nxsheet import VERSION; print(VERSION)')"
ARCH="$(dpkg --print-architecture)"

if [ ! -d "${SOURCE_DIR}" ]; then
    echo "Bundle not found: ${SOURCE_DIR}" >&2
    echo "Run 'python3 build_installers.py --platform linux' first." >&2
    exit 1
fi

if ! command -v dpkg-deb >/dev/null 2>&1; then
    echo "dpkg-deb is required to build a .deb package." >&2
    exit 1
fi

STAGE="$(mktemp -d)"
trap 'rm -rf "${STAGE}"' EXIT

PKG_ROOT="${STAGE}/nexuzy-sheet_${VERSION}_${ARCH}"
mkdir -p "${PKG_ROOT}/DEBIAN" \
         "${PKG_ROOT}/opt/nexuzy-sheet" \
         "${PKG_ROOT}/usr/bin" \
         "${PKG_ROOT}/usr/share/applications" \
         "${PKG_ROOT}/usr/share/icons/hicolor/256x256/apps" \
         "${PKG_ROOT}/usr/share/doc/nexuzy-sheet"

cp -R "${SOURCE_DIR}/." "${PKG_ROOT}/opt/nexuzy-sheet/"

cat > "${PKG_ROOT}/usr/bin/nexuzy-sheet" <<'WRAPPER'
#!/bin/sh
exec /opt/nexuzy-sheet/nexuzy-sheet "$@"
WRAPPER
chmod 755 "${PKG_ROOT}/usr/bin/nexuzy-sheet"

cp installers/linux/nexuzy-sheet.desktop \
   "${PKG_ROOT}/usr/share/applications/nexuzy-sheet.desktop"
cp assets/logo.png \
   "${PKG_ROOT}/usr/share/icons/hicolor/256x256/apps/nexuzy-sheet.png"
cp LICENSE "${PKG_ROOT}/usr/share/doc/nexuzy-sheet/copyright"

cat > "${PKG_ROOT}/DEBIAN/control" <<CONTROL
Package: nexuzy-sheet
Version: ${VERSION}
Section: office
Priority: optional
Architecture: ${ARCH}
Maintainer: Nexuzy Lab <support@nexuzy.in>
Homepage: https://nexuzy.in
Depends: libc6, libgl1, libegl1, libxkbcommon-x11-0, libxcb-cursor0
Description: Excel-like spreadsheet workspace
 Nexuzy Sheet is a spreadsheet application for business data, templates,
 calculations, exports, charts and local AI assisted workflows.
CONTROL

mkdir -p "${OUT_DIR}"
dpkg-deb --root-owner-group --build "${PKG_ROOT}" \
    "${OUT_DIR}/Nexuzy-Sheet-${VERSION}-linux-${ARCH}.deb"

echo "Created ${OUT_DIR}/Nexuzy-Sheet-${VERSION}-linux-${ARCH}.deb"
