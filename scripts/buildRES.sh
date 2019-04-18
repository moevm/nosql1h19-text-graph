#!/usr/bin/env bash
if ! [[ -d src ]]; then
    cd ..
fi
source venv/bin/activate;
if ! [[ -d src/res_compiled ]]; then
    mkdir src/res_compiled;
fi
rm -rf src/res_compiled/*;
for filename in res/*.qrc; do
    echo Converting ${filename:4:-4}_rc.py;
    pyrcc5 ${filename} >> src/res_compiled/${filename:4:-4}_rc.py;
done;
