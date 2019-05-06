#!/usr/bin/env bash
if ! [[ -d src ]]; then
    cd ..
fi
source venv/bin/activate;
cd src;
coverage run --source=api,models -m unittest
if ! [[ -d ../docs/coverage ]]; then
    mkdir ../docs/coverage;
fi
rm -rf ../docs/coverage/*;
coverage html --directory=../docs/coverage;
coverage xml -o ../docs/coverage.xml;
sensible-browser ../docs/coverage/index.html;
