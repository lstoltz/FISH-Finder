import tkinter as tk
from tkinter import Tk, Label, Button, filedialog, StringVar
import pandas as pd
import process_files as pf
import os
import glob
from process_files import dataSource, filePath, tempThreshold, loggerNumber

pf.main()

def cleanBadData():
        for file in dataSource:
            if file.endswith('.csv'):
                df = pd.read_csv(file)
                df = df.drop(df[df['DO Temperature (C)'] > tempThreshold].index)
                df = df.drop(df.head(2).index)
                df = df.drop(df.tail(2).index)
                df.to_csv(filePath, index = False)

def calCsvFiles():
    for logger in loggerNumber:
        #print(logger)
        for file in dataSource: # print issue where the letters are itemized and not lists of file paths
            print(file)
            if file.endswith('.csv'):
                
                fileOnDeck = glob.glob(logger)
                

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
        self.loggerLabel = Label(master, textvariable=self.currentLoggerLabel, font = ('helvetica', 12, 'bold'))
        # self.label.bind("<Button-1>", self.cycleLoggerText)
        self.loggerLabel.place(relx = 0.2, rely = 0.7)

        self.browseButton_preCsv = tk.Button(master,text="      Select pre-deployment cal file     ", command=self.getPreCsv, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.browseButton_preCsv.place(relx = 0.08, rely = 0.1)
        

        self.browseButton_postCsv = tk.Button(master,text="     Select post-deployment cal file     ", command=self.getPostCsv, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.browseButton_postCsv.place(relx = 0.08, rely = 0.3)

        self.calButton = tk.Button(master,text="     Calibrate!     ", command=self.calDataFiles, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.calButton.bind("<Button-1>", self.cycleLoggerText)
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

    def calDataFiles(self):
        cleanBadData()
    # for all loggers of getLoggerNumber() apply data cleaning then calibration factor

    # def cleanBadData(self):
    #     for file in dataSource:
    #         if file.endswith('.csv'):
    #             df = pd.read_csv(file)
    #             df = df.drop(df[df['DO Temperature (C)'] > tempThreshold].index)
    #             df = df.drop(df.head(2).index)
    #             df = df.drop(df.tail(2).index)
    #             df.to_csv(filePath, index = False)

    
    def cycleLoggerText(self, event):
        self.currentLoggerIndex += 1
        self.currentLoggerIndex %= len(self.LOGGER_TEXT) # wrap around
        self.currentLoggerLabel.set(self.LOGGER_TEXT[self.currentLoggerIndex])

    def getLoggerNumber(self):
        global loggerNumber
        loggerNumber = []
        for file in dataSource:
            print(file)
            if file.endswith('.csv'):
                fileName, fileExtension = os.path.splitext(filePath)
                #loggerNumber.append(fi)
                loggerNumber.append(fileName[:7])
        
    def clientExit(self):
        exit()

root = Tk()
def task():
    pf.main()
    calCsvFiles()
    print("hello")  # pt. 1: lets function be run alongside GUI in mainloop
    # root.after(2000, task) ## loops every 2 seconds

root.geometry("850x500")
CalibrationProgram = FishFinder(root)

root.after(2000, task) # pt. 2 
root.mainloop()