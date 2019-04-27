import nltk
import os
from PyInstaller.utils.hooks import collect_data_files

def modify_hooks(hooks):
    del hooks[0]

# add datas for nltk
datas = collect_data_files('nltk', False)

# loop through the data directories and add them
for p in nltk.data.path:
    if os.path.exists(p):
        datas.append((p, "nltk_data"))

# nltk.chunk.named_entity should be included
hiddenimports = ["nltk.chunk.named_entity"]
