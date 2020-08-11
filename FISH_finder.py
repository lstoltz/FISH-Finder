import tkinter as tk
from tkinter import Tk, Label, Button, filedialog, StringVar
import pandas as pd
import os, fnmatch, ntpath
from process_files import dataSource, tempThreshold

def getLoggerNumber():
    loggerNumber = None
    loggers = []

    for path, subdirs, files in os.walk(dataSource):
        for file in files:

            if file.endswith(".csv"):
                loggers.append(file[:7])
                loggerNumber = list(set(loggers))      

    return loggerNumber
                
def cleanBadData(files):
    df = pd.read_csv(files)
    df = df.drop(df[df['DO Temperature (C)'] > tempThreshold].index)
    df = df.drop(df.head(2).index)
    df = df.drop(df.tail(2).index)
    df.to_csv(files, index = False)
    print("it worked")

def applyCalibration(files):
    # add 3 point calibration from two dataframes
    pass
    
                 
class FishFinder:
    LOGGER_TEXT = getLoggerNumber()

    def __init__(self,master):
        self.master = master
        master.title("FISH Finder")
        self.snLabel = Label(master, text = "Logger SN that is being calibrated:", font = ('helvetica', 12))
        self.snLabel.place(relx = 0.12, rely = 0.5)
        self.currentLoggerIndex = 0
        self.currentLoggerLabel = StringVar() 
        self.currentLoggerLabel.set(self.LOGGER_TEXT[self.currentLoggerIndex])

        self.listBox = tk.Listbox(master, width=30)
        for file in self.getFiles():
            print("file:" + file)
            self.listBox.insert(tk.END, ntpath.basename(file))
        self.listBox.place(relx = 0.6, rely = 0.2)

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
        global currentLogger, loggerValue
        loggerValue = self.currentLoggerLabel.get()
        for files in os.listdir(dataSource):
            macFolders = os.path.join(dataSource, files)

            for file in os.listdir(macFolders):
                filePath = os.path.join(macFolders, file)
                fileName, fileExtension = os.path.splitext(filePath)

                if (fileExtension == ".csv"):
                    csvFiles = [filePath]
                    currentLogger = fnmatch.filter(csvFiles, str('*'+loggerValue+'*'))
                    #print(currentLogger)
                    for files in currentLogger:
                        cleanBadData(files)
                    # currentLogger = list(filter(None, currentLogger))   

    def getFiles(self): 
        global currentLogger, loggerValue
        loggerValue = self.currentLoggerLabel.get()
        for files in os.listdir(dataSource):
            macFolders = os.path.join(dataSource, files)

            csvFiles = []
            for file in os.listdir(macFolders):
                filePath = os.path.join(macFolders, file)
                fileName, fileExtension = os.path.splitext(filePath)

                if (fileExtension == ".csv"):
                    csvFiles.append(filePath)
            
            print(csvFiles)
            return csvFiles

        
    def calButtonCallback(self):
        self.calDataFiles()
        self.cycleLoggerText()

    def clientExit(self):
        exit()

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