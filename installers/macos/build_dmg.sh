#!/usr/bin/env bash
# Copyright (c) 2026 Nexuzy Lab
# Nexuzy Sheet - creates a drag and drop macOS disk image from the app bundle.
#
# Usage:  ./installers/macos/build_dmg.sh ["dist/Nexuzy Sheet.app"] [output dir]
# --------------------------------------------------------------------

set -euo pipefail

APP_PATH="${1:-dist/Nexuzy Sheet.app}"
OUT_DIR="${2:-dist/installers}"
VERSION="$(python3 -c 'from nxsheet import VERSION; print(VERSION)')"
DMG_PATH="${OUT_DIR}/Nexuzy-Sheet-${VERSION}-macos.dmg"

if [ ! -d "${APP_PATH}" ]; then
    echo "App bundle not found: ${APP_PATH}" >&2
    echo "Run 'python3 build_installers.py --platform macos' first." >&2
    exit 1
fi

STAGE="$(mktemp -d)"
trap 'rm -rf "${STAGE}"' EXIT

cp -R "${APP_PATH}" "${STAGE}/Nexuzy Sheet.app"
ln -s /Applications "${STAGE}/Applications"
cp LICENSE "${STAGE}/LICENSE" 2>/dev/null || true

mkdir -p "${OUT_DIR}"
rm -f "${DMG_PATH}"

hdiutil create \
    -volname "Nexuzy Sheet" \
    -srcfolder "${STAGE}" \
    -ov -format UDZO \
    "${DMG_PATH}"

echo "Created ${DMG_PATH}"
