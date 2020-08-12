import tkinter as tk
from tkinter import Tk, Label, Button, filedialog, StringVar
import pandas as pd
import os, fnmatch, ntpath
from process_files import dataSource, tempThreshold, dataDestination
from pathlib import Path

def getLoggerNumber():
    loggers = []
    loggerNumber = []

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
    #print("it worked")

def applyCalibration(files):
    # add 3 point calibration from two dataframes
    pass

def getListOfFiles(dataSource):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dataSource)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dataSource, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles
                
def cleanUpEmptyDir(macFolders):
    if (len(os.listdir(macFolders)) == 0):
        os.rmdir(macFolders)
class FishFinder(tk.Tk):
    LOGGER_TEXT = getLoggerNumber()

    def __init__(self,master):
        self.master = master
        master.title("FISH Finder")
       # self.startUpWindow = tk.Toplevel(master)
       # self.dataSource = tk.Button(master,text="      Select pre-deployment cal file     ", command=self.getPreCsv, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))




        self.snLabel = Label(master, text = "Logger SN that is being calibrated:", font = ('helvetica', 12))
        self.snLabel.place(relx = 0.12, rely = 0.7)
        self.currentLoggerIndex = 0
        self.currentLoggerLabel = StringVar() 
        self.currentLoggerLabel.set(self.LOGGER_TEXT[self.currentLoggerIndex])


        self.loggerLabel = Label(master, textvariable=self.currentLoggerLabel, font = ('helvetica', 12, 'bold'))
        self.loggerLabel.pack()
        self.loggerLabel.place(relx = 0.2, rely = 0.8)

        self.listBox = tk.Listbox(master, width=40, height=15)
        for file in self.getFiles():
            #print("file:" + file)
            self.listBox.insert(tk.END, ntpath.basename(file))
        self.listBox.place(relx = 0.6, rely = 0.1)

        self.listBoxLabel = tk.Label(master, fg = "black", text = "Files to be Processed", font =('helvetica', 12, 'bold') )
        self.listBoxLabel.place(relx = 0.6, rely = 0.05)

        self.preCsvLabel = tk.Label(master, fg="red", text="No file selected.", font =('helvetica', 12) )  
        self.preCsvLabel.place(relx = 0.08, rely = 0.2) 
        self.browseButton_preCsv = tk.Button(master,text="      Select pre-deployment cal file     ", command=self.getPreCsv, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.browseButton_preCsv.place(relx = 0.08, rely = 0.1)
 
          
        self.postCsvLabel = tk.Label(master, fg="red", text="No file selected.", font =('helvetica', 12)) 
        self.postCsvLabel.place(relx = 0.08, rely = 0.48)
        self.browseButton_postCsv = tk.Button(master,text="     Select post-deployment cal file     ", command=self.getPostCsv, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.browseButton_postCsv.place(relx = 0.08, rely = 0.37)
 
        
        self.calButton = tk.Button(master,text="     Calibrate!     ", command=self.calButtonCallback, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.calButton.place(relx = 0.7, rely = 0.7)


    def getPreCsv(self):
        global df_pre
        import_file_path = filedialog.askopenfilename()
        self.preCsvLabel.config(text=ntpath.basename(import_file_path), fg = "black", font =('helvetica', 12))
        df_pre = pd.read_csv (import_file_path)
        print (df_pre)
    
    def getPostCsv(self):
        global df_post
        import_file_path = filedialog.askopenfilename()
        self.postCsvLabel.config(text=ntpath.basename(import_file_path), fg = "black", font =('helvetica', 12))
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
                        applyCalibration(files)
                        self.moveFiles()
                        #print(files)
                    # currentLogger = list(filter(None, currentLogger))   
                    
    def moveFiles(self):
        loggerValue = self.currentLoggerLabel.get()
        listOfFiles = getListOfFiles(dataSource)
        # for path, subdirs, files in os.walk(dataSource):
        # for file in filePath:
        #     print(filePath)
        for files in listOfFiles:
            #print(files)
            filesToMove = fnmatch.filter(files, str('*'+loggerValue+'*'))
            for file in filesToMove:

                filename = ntpath.basename(file)
                folderStructure = files.split(os.path.sep)
                Path(dataDestination + os.path.sep + folderStructure[-2] + os.path.sep).mkdir(parents=True, exist_ok=True)
                os.rename(file, dataDestination + os.path.sep + folderStructure[-2] + os.path.sep + filename)   
                #print(folderStructure)

    def getFiles(self): 
        global currentLogger, loggerValue
        loggerValue = self.currentLoggerLabel.get()

        csvFiles = []
        for path, subdirs, files in os.walk(dataSource):
            for file in files:

                if file.endswith(".csv"):
                    csvFiles.append(file)

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

root.geometry("1200x700")
CalibrationProgram = FishFinder(root)

#root.after(2000, task) # pt. 2 
root.mainloop()