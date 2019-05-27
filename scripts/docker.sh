for filename in ui_files/*.ui; do
    pyuic5 ${filename} --import-from res_compiled >> ./ui_compiled/${filename:9:-3}.py; 
done;
for filename in res_files/*.qrc; do
    pyrcc5 ${filename} >> ./res_compiled/${filename:10:-4}_rc.py;
done;
