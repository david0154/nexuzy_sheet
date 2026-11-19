#!/usr/bin/env bash
# Copyright (c) 2026 Nexuzy Lab
# Nexuzy Sheet - builds an AppImage from the PyInstaller bundle.
#
# Requires appimagetool:
#   https://github.com/AppImage/AppImageKit/releases
#
# Usage:  ./installers/linux/build_appimage.sh [dist/nexuzy-sheet] [output dir]
# --------------------------------------------------------------------

set -euo pipefail

SOURCE_DIR="${1:-dist/nexuzy-sheet}"
OUT_DIR="${2:-dist/installers}"
VERSION="$(python3 -c 'from nxsheet import VERSION; print(VERSION)')"

if [ ! -d "${SOURCE_DIR}" ]; then
    echo "Bundle not found: ${SOURCE_DIR}" >&2
    echo "Run 'python3 build_installers.py --platform linux' first." >&2
    exit 1
fi

APPIMAGETOOL="${APPIMAGETOOL:-$(command -v appimagetool || true)}"
if [ -z "${APPIMAGETOOL}" ]; then
    echo "appimagetool not found. Download it and put it into PATH." >&2
    echo "Alternatively run: python3 build_installers.py --no-native" >&2
    exit 1
fi

APPDIR="${PWD}/build/NexuzySheet.AppDir"
rm -rf "${APPDIR}"
mkdir -p "${APPDIR}/usr/bin" "${APPDIR}/usr/share/applications" \
         "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

cp -R "${SOURCE_DIR}/." "${APPDIR}/usr/bin/"
cp installers/linux/AppRun "${APPDIR}/AppRun"
chmod 755 "${APPDIR}/AppRun"
cp installers/linux/nexuzy-sheet.desktop "${APPDIR}/nexuzy-sheet.desktop"
cp installers/linux/nexuzy-sheet.desktop \
   "${APPDIR}/usr/share/applications/nexuzy-sheet.desktop"
cp assets/logo.png "${APPDIR}/nexuzy-sheet.png"
cp assets/logo.png \
   "${APPDIR}/usr/share/icons/hicolor/256x256/apps/nexuzy-sheet.png"
cp LICENSE "${APPDIR}/LICENSE"

mkdir -p "${OUT_DIR}"
ARCH="$(uname -m)" "${APPIMAGETOOL}" "${APPDIR}" \
    "${OUT_DIR}/Nexuzy-Sheet-${VERSION}-linux-${ARCH}.AppImage"

echo "Created ${OUT_DIR}/Nexuzy-Sheet-${VERSION}-linux-${ARCH}.AppImage"
