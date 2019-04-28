#!/usr/bin/env bash
if ! [[ -d venv ]]; then
    cd ..
fi
source venv/bin/activate;
if [[ -d build ]]; then
    rm -rf build
fi
if [[ -d dist ]]; then
    rm -rf dist
fi

echo "Warning, overriding PyInstaller NLTK hook"
pyi_path="$(python -c 'import PyInstaller; print(PyInstaller.__file__[:-11])')"
echo "PyInstaller path: ${pyi_path}"

yes | cp hooks/hook-nltk.py ${pyi_path}hooks
yes | cp ${pyi_path}loader/rthooks/pyi_rth__nltk.py ${pyi_path}loader/rthooks/pyi_rth_nltk.py

paths=(
    src/
    src/api/
    src/api/algorithm/
    src/api/database/   
    src/config/
    src/models/
    src/res_compiled/
    src/ui/
    src/ui/graph/
    src/ui/misc/
    src/ui/widgets/
    src/ui_compiled/
)

final_path=""

for i in "${paths[@]}"; do
    final_path=${final_path}:${i}
done
#echo ${final_path:1}
pyinstaller src/main.py --paths=${final_path:1} --additional-hooks-dir=hooks/ --onefile
