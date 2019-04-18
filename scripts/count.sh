#!/usr/bin/env bash
if ! [[ -d src ]]; then
    cd ..
fi

cloc scripts src --exclude-dir=ui_compiled,res_compiled
