#!/usr/bin/env bash
if ! [[ -d src ]]; then
    cd ..
fi
source venv/bin/activate
cd src
tests=""
for filename in tests/test_*.py; do
    tests=${tests},${filename:6}
done;
tests=${tests:1},config.py,prebuilt.py
pyreverse . -o png -A -p text_graph -s 2 --ignore=${tests}
