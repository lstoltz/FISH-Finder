import pandas as pd
import numpy as np
import glob
import os, ntpath, re
from pathlib import Path
import shutil

dataSource = r'C:\Users\lstol\Documents\Repositories\clean-data\inbox'
dataDestination = r'C:\Users\lstol\Documents\Repositories\clean-data\outbox'
dataFlagged = r'C:\Users\lstol\Documents\Repositories\clean-data\flagged'
tempThreshold = 10 # Threshold for when to subset temperature (In celcius)
macFolders = None
