import tkinter as tk
from tkinter import Tk, Label, Button, filedialog, StringVar
import pandas as pd
import os, fnmatch, ntpath, shutil
from pathlib import Path

# dataSource = r'C:\Users\lstol\Documents\Repositories\clean-data\inbox'
# dataDestination = r'C:\Users\lstol\Documents\Repositories\clean-data\outbox'  # temporary variables, when shipping final product delete and rely on UI
# dataFlagged = r'C:\Users\lstol\Documents\Repositories\clean-data\flagged'
tempThreshold = 10 # Threshold for when to subset temperature (In celcius)

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
    print("it worked")

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
    try:
        if (len(os.listdir(macFolders)) == 0):
            os.rmdir(macFolders)
    except FileNotFoundError:
        pass



class StartPage(tk.Frame):

    def __init__(self, parent):
        self.parent = parent
        parent.title("FISH Finder")

        self.info = """Welcome to FISH Finder! 

        This program applies pre and post deployment calibration curves to data loggers and removes values out of range for Oregon.
        
        To proceed, please select the folder where data files are nested within
        their MAC address folders as well as a destination for calibrated files."""

        self.creator = """Created by Linus Stoltz"""

        self.dataSourceButton = tk.Button(parent, text="      Select Data Source     ", command=self.getDataSource, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.dataSourceButton.place(relx= 0.1, rely = 0.29)

        self.dataSourceLabel = tk.Label(parent, fg="red", text="No folder selected.", font =('helvetica', 12) )
        self.dataSourceLabel.place(relx = 0.05, rely = 0.4)

        self.dataDestButton = tk.Button(parent, text="      Select Data Destination     ", command=self.getDataDest, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.dataDestButton.place(relx= 0.6, rely = 0.3)

        self.dataDestLabel = tk.Label(parent, fg="red", text="No folder selected.", font =('helvetica', 12) )
        self.dataDestLabel.place(relx = 0.5, rely = 0.4)
        
        self.infoText = tk.Label(parent, text = self.info, font = ('helvetica', 11))
        # self.infoText.insert(tk.END, self.info)
        self.infoText.place(relx = 0.05, rely = 0.05)

        self.creatorText = tk.Label(parent, text = self.creator, font = ('helvetica', 11))
        # self.infoText.insert(tk.END, self.info)
        self.creatorText.place(relx = 0.05, rely = 0.9)


        self.errorLabel = tk.Label(parent, fg="red", text="Error: please select a data source and desination!", font =('helvetica', 12, 'bold') )

        self.nextPageButton = tk.Button(parent, text="      Next!     ", command=self.nextPage, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.nextPageButton.place(relx= 0.67, rely = 0.7)

    def getDataSource(self):
        global dataSource
        dataSource = filedialog.askdirectory()
        if dataSource == "":
            pass
        else:
            self.dataSourceLabel.config(text=dataSource, fg = "black", font =('helvetica', 12))

    def getDataDest(self):
        global dataDestination
        dataDestination = filedialog.askdirectory()
        if dataDestination == "":
            pass
        else:
            self.dataDestLabel.config(text=dataDestination, fg = "black", font =('helvetica', 12))
    
    def nextPage(self):
        try:
            if os.path.exists(dataSource) and os.path.exists(dataDestination):
                self.dataSourceButton.place_forget()
                self.dataDestButton.place_forget()
                self.nextPageButton.place_forget()
                self.dataSourceLabel.place_forget()
                self.dataDestLabel.place_forget()
                self.errorLabel.place_forget()
                self.infoText.place_forget()
                self.creatorText.place_forget()
                CalibrationProgram = SecondPage(root)

        except NameError:
            self.errorLabel.place(relx= 0.04, rely = 0.5)
        
class SecondPage(tk.Frame):

    def __init__(self,master):
        self.master = master
        master.title("FISH Finder")

        self.LOGGER_TEXT = self.getLoggerNumber()
        self.snLabel = Label(master, text = "Logger SN that is being calibrated:", font = ('helvetica', 12))
        self.snLabel.place(relx = 0.12, rely = 0.7)
        self.currentLoggerIndex = 0
        self.currentLoggerLabel = StringVar()

        self.fatalErrMsg = """Error: Data source folder contains no data, or has a folder structure not supported by this program. 
        Don't panic, close the program, check the folder, and try again!"""

        self.emptyInboxErrorlabel = Label(master, text = self.fatalErrMsg, fg = 'red', font = ('helvetica', 12, 'bold'))

        self.loggersDoneLabel = tk.Label(master, text = "All loggers successfully calibrated! Please close this window", fg = 'green', font = ('helvetica', 12, 'bold'))
        
        self.loggerLabel = Label(master, textvariable=self.currentLoggerLabel, font = ('helvetica', 12, 'bold'))
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

        try:
            self.currentLoggerLabel.set(self.LOGGER_TEXT[self.currentLoggerIndex])
        except IndexError:
            self.emptyInboxErrorlabel.place(relx = 0.1, rely = 0.5)
            self.listBox.place_forget()
            self.postCsvLabel.place_forget()
            self.listBoxLabel.place_forget()
            self.preCsvLabel.place_forget()
            self.browseButton_postCsv.place_forget()
            self.browseButton_preCsv.place_forget()
            self.snLabel.place_forget()
            self.calButton.place_forget()


    def getPreCsv(self):
        global df_pre
        import_file_path = filedialog.askopenfilename()
        if import_file_path == "":
            pass
        else:
            self.preCsvLabel.config(text=ntpath.basename(import_file_path), fg = "black", font =('helvetica', 12))
            df_pre = pd.read_csv (import_file_path)
            print (df_pre)
    
    def getPostCsv(self):
        global df_post
        # try:
        import_file_path = filedialog.askopenfilename()
        if import_file_path == "":
            pass
        else:
            self.postCsvLabel.config(text=ntpath.basename(import_file_path), fg = "black", font =('helvetica', 12))
            df_post = pd.read_csv (import_file_path)
            print (df_post)

    def getLoggerNumber(self):
        loggers = []
        loggerNumber = []
        for path, subdirs, files in os.walk(dataSource):
            for file in files:

                if file.endswith(".csv"):
                    loggers.append(file[:7])
                    loggerNumber = list(set(loggers))      
        
        return loggerNumber


    
    def cycleLoggerText(self):
        try:
            self.currentLoggerIndex += 1
            #self.currentLoggerIndex %= len(self.LOGGER_TEXT) # wrap around
            self.currentLoggerLabel.set(self.LOGGER_TEXT[self.currentLoggerIndex])
                
        except IndexError:
            self.loggerLabel.place_forget()
            self.snLabel.place_forget() 
            self.loggersDoneLabel.place(relx = 0.1, rely = 0.8)
              

    def calDataFiles(self):
        global currentLogger, loggerValue, macFolders
        loggerValue = self.currentLoggerLabel.get()
        for files in os.listdir(dataSource):
            macFolders = os.path.join(dataSource, files)
            for file in os.listdir(macFolders):
                filePath = os.path.join(macFolders, file)
                fileName, fileExtension = os.path.splitext(filePath)

                if (fileExtension == ".csv"):
                    csvFiles = [filePath]
                    currentLogger = fnmatch.filter(csvFiles, str('*'+loggerValue+'*'))
                    for files in currentLogger:
                        
                        cleanBadData(files)
                        applyCalibration(files)

        self.moveFiles()
        cleanUpEmptyDir(macFolders)

    def cleanBadData(self, files):
        df = pd.read_csv(files)
        df = df.drop(df[df['DO Temperature (C)'] > tempThreshold].index)
        df = df.drop(df.head(2).index)
        df = df.drop(df.tail(2).index)
        df.to_csv(files, index = False)
        print("it worked")

    def applyCalibration(self, files):
        # add 3 point calibration from two dataframes
        pass
  
                    
    def moveFiles(self):
        loggerValue = self.currentLoggerLabel.get()
        listOfFiles = getListOfFiles(dataSource)
        fileQueue = []      
        fileQueue.append(fnmatch.filter(listOfFiles, str('*'+loggerValue+'*')))
        for files in fileQueue:
            for file in files:
                filename = ntpath.basename(file)
                folderStructure = file.split(os.path.sep)
                Path(dataDestination + os.path.sep + folderStructure[-2] + os.path.sep).mkdir(parents=True, exist_ok=True)
                os.rename(file, dataDestination + os.path.sep + folderStructure[-2] + os.path.sep + filename)

        self.listBox.delete(0, tk.END)
        for file in self.getFiles():
            #print("file:" + file)
            self.listBox.insert(tk.END, ntpath.basename(file))
         
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
        cleanUpEmptyDir(macFolders)
        
    def clientExit(self):
        exit()


root = Tk()
root.geometry("1200x700")

# dataSource = r'C:\Users\lstol\Documents\Repositories\clean-data\inbox'  ## Uncover these three to skip the start page
# dataDestination = r'C:\Users\lstol\Documents\Repositories\clean-data\outbox'
# StartUpScreen = SecondPage(root)

FishFinder = StartPage(root)

root.mainloop()