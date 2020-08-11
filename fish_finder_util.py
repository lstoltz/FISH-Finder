import os, fnmatch
import pandas as pd
from process_files import dataSource
from process_files import tempThreshold


def getLoggerNumber():
    global loggerNumber
    loggers = []

    for path, subdirs, files in os.walk(dataSource):
        for file in files:

            if file.endswith(".csv"):
                loggers.append(file[:7])
                loggerNumber = list(set(loggers))

                #print(loggerNumber)

def findFiles():
    global dataSource, fileName, filePath, macFolders
    
    for files in os.listdir(dataSource):
        macFolders = os.path.join(dataSource, files)

        for file in os.listdir(macFolders):
            filePath = os.path.join(macFolders, file)
            fileName, fileExtension = os.path.splitext(filePath)
            #print(filePath)

            if (fileExtension == ".csv"):
                csvFiles = filePath
                cleanBadData()
                #print(csvFiles)
                #selectDataFiles(csvFiles)
                
        
def cleanBadData():
    df = pd.read_csv(filePath)
    df = df.drop(df[df['DO Temperature (C)'] > tempThreshold].index)
    df = df.drop(df.head(2).index)
    df = df.drop(df.tail(2).index)
    df.to_csv(filePath, index = False)


def selectDataFiles(csvFiles):
    for logger in loggerNumber:
        if fnmatch.fnmatch(csvFiles, [logger]):
           # print(csvFiles)
           pass
        
def main():
    getLoggerNumber()
    findFiles()

main()