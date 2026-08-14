#!/bin/bash

set -e

HERE_DIR=`dirname "$BASH_SOURCE"`
ROOT_DIR=`realpath $HERE_DIR/..`

echo "ROOT_DIR=$ROOT_DIR"

# Make pyspread importable for autodoc
export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"

# (Re)generate per-module API rst files so newly added modules are picked up.
# Exclude test directories so they do not show up in the toctree (they are
# also listed in conf.py's exclude_patterns to skip building them).
sphinx-apidoc -f -o "$ROOT_DIR/apidocs" "$ROOT_DIR/pyspread" \
    "$ROOT_DIR/pyspread/test" "$ROOT_DIR/pyspread/*/test"

sphinx-build -a -b html "$ROOT_DIR/apidocs" "$ROOT_DIR/public/"
