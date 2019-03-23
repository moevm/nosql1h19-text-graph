#!/usr/bin/env bash
cd ..
source venv/bin/activate;
if [[ -d build ]]; then
    rm -rf build
fi
if [[ -d dist ]]; then
    rm -rf dist
fi

paths=(
    src/
    src/api/
    src/config/
    src/models/
    src/res_compiled/
    src/ui_compiled
)

final_path=""

for i in "${paths[@]}"; do
    final_path=${final_path}:${i}
done
#echo ${final_path:1}
pyinstaller src/main.py --paths=${final_path:1} --additional-hooks-dir=hooks/