import os
import pandas
rootdir = r"C:\Users\lstol\Documents\Repositories\clean-data\inbox"

for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        print(os.path.join(subdir, file))
