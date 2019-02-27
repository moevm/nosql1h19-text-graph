#!/usr/bin/env bash
source venv/bin/activate;
if ! [[ -d src/res ]]; then
    mkdir src/res;
fi
rm -rf src/res/*;
for filename in res/*.qrc; do
    echo Converting ${filename:4:-4}_rc.py;
    pyrcc5 ${filename} >> src/res/${filename:4:-4}_rc.py;
done;