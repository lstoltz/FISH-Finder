import tkinter as tk
from tkinter import Tk, Label, Button, filedialog, StringVar
import pandas as pd
import process_files as pf
import os
import glob
import fnmatch
from process_files import dataSource, filePath, tempThreshold
from fish_finder_util import loggerNumber


def findFiles():
    global dataSource, fileName, filePath, macFolders
    
    for files in os.listdir(dataSource):
        macFolders = os.path.join(dataSource, files)

        for file in os.listdir(macFolders):
            filePath = os.path.join(macFolders, file)
            fileName, fileExtension = os.path.splitext(filePath)

            if (fileExtension == ".csv"):
                csvFiles = fileName
                cleanBadData()
                selectDataFiles(csvFiles)
                
                
def cleanBadData():
    df = pd.read_csv(filePath)
    df = df.drop(df[df['DO Temperature (C)'] > tempThreshold].index)
    df = df.drop(df.head(2).index)
    df = df.drop(df.tail(2).index)
    df.to_csv(filePath, index = False)


# def selectDataFiles(csvFiles):
#     for logger in loggerNumber:
        
#         if logger in csvFiles:
#             pass
#            # print(csvFiles)
        
                
            
          
class FishFinder:
    LOGGER_TEXT = loggerNumber

    def __init__(self,master):
        self.master = master
        master.title("FISH Finder")
        self.snLabel = Label(master, text = "Logger SN that is being calibrated:", font = ('helvetica', 12))
        self.snLabel.place(relx = 0.12, rely = 0.5)
        self.currentLoggerIndex = 0
        self.currentLoggerLabel = StringVar() 
        self.currentLoggerLabel.set(self.LOGGER_TEXT[self.currentLoggerIndex])

        #print(loggerValue)
        self.loggerLabel = Label(master, textvariable=self.currentLoggerLabel, font = ('helvetica', 12, 'bold'))
        self.loggerLabel.place(relx = 0.2, rely = 0.7)
        
        

        self.browseButton_preCsv = tk.Button(master,text="      Select pre-deployment cal file     ", command=self.getPreCsv, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.browseButton_preCsv.place(relx = 0.08, rely = 0.1)        

        self.browseButton_postCsv = tk.Button(master,text="     Select post-deployment cal file     ", command=self.getPostCsv, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.browseButton_postCsv.place(relx = 0.08, rely = 0.3)
        
        self.calButton = tk.Button(master,text="     Calibrate!     ", command=self.calButtonCallback, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.calButton.place(relx = 0.7, rely = 0.7)


    def getPreCsv(self):
        global df_pre
        import_file_path = filedialog.askopenfilename()
        df_pre = pd.read_csv (import_file_path)
        print (df_pre)
    
    def getPostCsv(self):
        global df_post
        import_file_path = filedialog.askopenfilename()
        df_post = pd.read_csv (import_file_path)
        print (df_post)
    
    def cycleLoggerText(self):
        self.currentLoggerIndex += 1
        self.currentLoggerIndex %= len(self.LOGGER_TEXT) # wrap around
        self.currentLoggerLabel.set(self.LOGGER_TEXT[self.currentLoggerIndex])        

    def calDataFiles(self):
        self.getCurrentLogger()
        
    def calButtonCallback(self):
        self.calDataFiles()
        self.cycleLoggerText()

    def clientExit(self):
        exit()

    def getCurrentLogger(self):
        global currentLogger
        loggerValue = self.currentLoggerLabel.get()
        for files in os.listdir(dataSource):
            macFolders = os.path.join(dataSource, files)

            for file in os.listdir(macFolders):
                filePath = os.path.join(macFolders, file)
                fileName, fileExtension = os.path.splitext(filePath)

                if (fileExtension == ".csv"):
                    csvFiles = [filePath]
                    currentLogger = fnmatch.filter(csvFiles, str('*'+loggerValue+'*'))
                    currentLogger = list(filter(None, currentLogger))
                    print(currentLogger)

root = Tk()
def task():
    #findFiles()
    #print(loggerNumber)
    #calCsvFiles()
    print("hello")  # pt. 1: lets function be run alongside GUI in mainloop

root.geometry("850x500")
CalibrationProgram = FishFinder(root)

#root.after(2000, task) # pt. 2 
root.mainloop()