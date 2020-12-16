import os
from urllib.parse import unquote

folder = "./mp3"
file_names = os.listdir(folder)
for file_name in file_names:
    if file_name != unquote(file_name):
        os.rename(os.path.join(folder, file_name),
                  os.path.join(folder, unquote(file_name)))
        print(f"{file_name} renamed to {unquote(file_name)}")
