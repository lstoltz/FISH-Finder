import pandas as pd
import numpy as np
import glob
import os, ntpath, uuid, re
from pathlib import Path
from datetime import datetime

dataSource = r"C:\Users\lstol\Documents\Repositories\clean-data\inbox"
datDestination = r"C:\Users\lstol\Documents\Repositories\clean-data\outbox"


def findFiles():
    global dataSource
    for files in os.listdir(dataSource):
        dataFiles = os.path.join(dataSource, files)

        processCSV(dataFiles)
        cleanUpEmptyDir(dataFiles)

def processCSV(dataFiles):
    for file in os.listdir(dataFiles):
        filePath = os.path.join(dataFiles, file)
        fileName, fileExtension = os.path.splitext(filePath)

        if (fileExtension == ".csv"):
            getLoggerNumber(os.path.basename(fileName))
            cleanData(fileName, dataFiles)

def cleanData(fileName, dataFiles):
# Process and drop rows conditionally
    df = pd.read_csv(dataFiles)
    print(df)


def getLoggerNumber(filename):
    global loggerNumber

    loggerNumber = filename[:7]

def cleanUpEmptyDir(devicePath):
    if (len(os.listdir(devicePath)) == 0):
        os.rmdir(devicePath)


# file = r'C:\Users\lstol\Documents\Repositories\clean-data\inbox\04-ee-03-73-87-74\2002003_sxt_DissolvedOxygen.csv'
# df = pd.read_csv(file)
# print(len(df))
# df = df[df['DO Temperature (C)'] < 10]
# print(len(df))
# df.to_csv(data_destination + 'test.csv', index = False)
