import pandas as pd
import numpy as np
import glob
import os, ntpath, uuid, re
from pathlib import Path
from datetime import datetime

dataSource = r'C:\Users\lstol\Documents\Repositories\clean-data\inbox'
datDestination = r'C:\Users\lstol\Documents\Repositories\clean-data\outbox'


def findFiles():
    global dataSource
    for files in os.listdir(dataSource):
        macFolders = os.path.join(dataSource, files)

        processCSV(macFolders)
        cleanUpEmptyDir(macFolders)

def processCSV(macFolders):
    for file in os.listdir(macFolders):
        filePath = os.path.join(macFolders, file)
        fileName, fileExtension = os.path.splitext(filePath)
        
        if (fileExtension == ".csv"):
            getLoggerNumber(os.path.basename(fileName))
            cleanData(filePath)

def cleanData(filePath):
# Process and drop rows conditionally
# Dropping based on % change from one temp obs to another??
   
    df = pd.read_csv(filePath)
    print(df)


def getLoggerNumber(filename):
    global loggerNumber

    loggerNumber = filename[:7]

def cleanUpEmptyDir(devicePath):
    if (len(os.listdir(devicePath)) == 0):
        os.rmdir(devicePath)

def main():
    findFiles()

main()

