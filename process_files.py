import pandas as pd
import numpy as np
import glob
import os
from pathlib import Path


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
        
        #if (fileExtension == ".gps"):
            # Check the gps file to make sure the locations are not NA,
            # If they are NA, move all three files to "flagged" dir 

def cleanData(filePath):
    df = pd.read_csv(filePath)
    print(df)
    # Process and drop rows conditionally
    # Dropping based on % change from one temp obs to another??     
    # Two steps, one to remove rows based on thresholds, next step removes 2 observations from both ends to gaurentee sensor is on the bottom 

def getLoggerNumber(filename):
    global loggerNumber

    loggerNumber = filename[:7]

def cleanUpEmptyDir(devicePath):
    if (len(os.listdir(devicePath)) == 0):
        os.rmdir(devicePath)

#def moveFiles(files):
 #   for file in files:
  #      filename = ntpath.basename(file)
   #     folderStructure = file.split(os.path.sep)
    #    Path(dataDestination + os.path.sep + folderStructure[-2] + os.path.sep).mkdir(parents=True, exist_ok=True)
     #   os.rename(file, dataDestination + os.path.sep + folderStructure[-2] + os.path.sep + filename)

def main():
    findFiles()

main()

