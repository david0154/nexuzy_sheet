#!/bin/bash
# Copyright (c) 2026 Nexuzy Lab
# Starts Nexuzy Sheet from the source tree on Linux.
# Licensed under the MIT License.
# --------------------------------------------------------------------

# Wayland workaround: avoid double triggered shortcuts
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"

cd "$(dirname "$0")" || exit 1
exec python3 -m nxsheet "$@"
