import os, fnmatch
import pandas as pd
from process_files import dataSource
from process_files import tempThreshold


def getLoggerNumber():
    loggers = []

    for path, subdirs, files in os.walk(dataSource):
        for file in files:

            if file.endswith(".csv"):
                loggers.append(file[:7])
                loggerNumber = list(set(loggers))
                
    return loggerNumber

# def findFiles():
#     global dataSource, fileName, filePath, macFolders
    
#     for files in os.listdir(dataSource):
#         macFolders = os.path.join(dataSource, files)

#         for file in os.listdir(macFolders):
#             filePath = os.path.join(macFolders, file)
#             fileName, fileExtension = os.path.splitext(filePath)
#             #print(filePath)

#             if (fileExtension == ".csv"):
#                 csvFiles = filePath
#                 cleanBadData()
                #print(csvFiles)
                #selectDataFiles(csvFiles)
                

        
def main():
    getLoggerNumber()
    # findFiles()

main()