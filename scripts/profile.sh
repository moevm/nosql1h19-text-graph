#!/usr/bin/env bash
if ! [[ -d src ]]; then
    cd ..
fi
source venv/bin/activate;
cd src
python -m cProfile -o ../docs/profile -s cumulative main.py
