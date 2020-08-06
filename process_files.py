import pandas as pd
import numpy as np
import glob
import os, ntpath, uuid, re
from pathlib import Path
from datetime import datetime

dataSource = r'C:\Users\lstol\Documents\Repositories\clean-data\inbox'
dataDestination = r'C:\Users\lstol\Documents\Repositories\clean-data\outbox'
dataFlagged = r'C:\Users\lstol\Documents\Repositories\clean-data\flagged'
tempThreshold = 10 # Threshold for when to subset temperature (In celcius)


def findFiles():
    global dataSource
    for files in os.listdir(dataSource):
        macFolders = os.path.join(dataSource, files)

        processCSV(macFolders)
        cleanUpEmptyDir(macFolders)

def checkLocation(fileName, macFolders):
    global gpsFilePath, lidFilePath, csvFilePath
    gpsFilePath = os.path.join(macFolders,fileName).replace("_DissolvedOxygen", "")+".gps"
    lidFilePath = os.path.join(macFolders,fileName).replace("_DissolvedOxygen", "")+".lid"
    csvFilePath = os.path.join(macFolders,fileName+".csv")

    with open(gpsFilePath) as fp:
        for cnt, line in enumerate(fp):
            if ("RWS" in line):
                rws = line.replace("RWS: ", "")
            elif ("SWS" in line):
                sws = line.replace("SWS: ", "")

        # Use appropriate value (default to SWS) and then split up lat/long
        if ("N/A" not in sws):
            endOfLatIndex = sws.find(".") + 7
            latitude = sws[0:endOfLatIndex]
            longitude = sws[endOfLatIndex:]
        elif ("N/A" not in rws):
            endOfLatIndex = rws.find(".") + 7
            latitude = rws[0:endOfLatIndex]
            longitude = rws[endOfLatIndex:]
        else:
            moveBadFiles([gpsFilePath, lidFilePath, csvFilePath])

def processCSV(macFolders):
    for file in os.listdir(macFolders):
        filePath = os.path.join(macFolders, file)
        fileName, fileExtension = os.path.splitext(filePath)

        if(fileExtension == ".gps"):
            pass

        if (fileExtension == ".csv"):
            getLoggerNumber(os.path.basename(fileName))
            cleanData(filePath)
            moveFiles([gpsFilePath, lidFilePath, filePath])      
        

def cleanData(filePath):  
    df = pd.read_csv(filePath)
    df = df.drop(df[df['DO Temperature (C)'] > tempThreshold].index)
    df = df.drop(df.head(2).index)
    df = df.drop(df.tail(2).index)
    df.to_csv(filePath, index = False)

def moveFiles(files):
    for file in files:
        filename = ntpath.basename(file)
        print(filename)
        folderStructure = file.split(os.path.sep)
        print(folderStructure)
        Path(dataDestination + os.path.sep + folderStructure[-3] + os.path.sep).mkdir(parents=True, exist_ok=True)
        os.rename(file, dataDestination + os.path.sep + folderStructure[-3] + os.path.sep + filename)

def moveBadFiles(files):
    for file in files:
        filename = ntpath.basename(file)
        folderStructure = file.split(os.path.sep)
        Path(dataFlagged + os.path.sep + folderStructure[-2] + os.path.sep).mkdir(parents=True, exist_ok=True)
        os.rename(file, dataFlagged + os.path.sep + folderStructure[-2] + os.path.sep + filename)


def getLoggerNumber(filename):
    global loggerNumber

    loggerNumber = filename[:7]

def cleanUpEmptyDir(macFolders):
    if (len(os.listdir(macFolders)) == 0):
        os.rmdir(macFolders)

def main():
    findFiles()

main()

