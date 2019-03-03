#!/usr/bin/env bash
cd ..
source venv/bin/activate;
if [[ -d build ]]; then
    rm -rf build
fi
if [[ -d dist ]]; then
    rm -rf dist
fi
pyinstaller src/main.py --paths=src/:src/config/:src/models/:src/ui/ --additional-hooks-dir=hooks/