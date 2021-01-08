import tkinter as tk
from tkinter import Tk, Label, Button, filedialog, StringVar
import pandas as pd
import os, fnmatch, ntpath, shutil
from pathlib import Path
import numpy as np
from sklearn.linear_model import LinearRegression
import csv
from matplotlib.dates import date2num as date2num

tempThreshold = 10 # Threshold for when to subset temperature (In celcius)
with open(r'calibration_parms.csv', 'a', newline='') as csvfile:
    fieldnames = ["logger_sn","pre_slope","pre_intcpt", "post_slope","post_intcpt",
    "pre_x1", "pre_x2","pre_x3","preStd_y1","preStd_y2","preStd_y3","post_x1","post_x2",
    "post_x3","postStd_y1","postStd_y2","postStd_y3", "t_pre", "t_post"]
    writer = csv.DictWriter(csvfile, fieldnames= fieldnames)
    writer.writeheader()
    

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
                

class StartPage(tk.Frame):   # setting up formatting for the first page of the program 

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

        self.nextPageButton = tk.Button(parent, text="Next!", command=self.nextPage, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'), padx = 30, pady = 18)
        self.nextPageButton.place(relx= 0.69, rely = 0.7)

    def getDataSource(self):  # where data that need to be cleaned/calibrated reside
        global dataSource
        dataSource = filedialog.askdirectory()
        
        if dataSource == "":
            pass
        else:
            self.dataSourceLabel.config(text=dataSource, fg = "black", font =('helvetica', 12))

    def getDataDest(self): # where data that are cleaned/calibrated are shuttled to when finished
        global dataDestination
        dataDestination = filedialog.askdirectory()
        self.errorLabel.place_forget()
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
        
class SecondPage(tk.Frame):  # this page is the work horse that performs the moving/cleaning/calibration

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

        self.timeMsgErr = """Error: Invalid time input"""
        self.timeMsglabel = tk.Label(master, text = self.timeMsgErr, fg = 'red', font = ('helvetica', 12, 'bold'))

        self.inputMsgErr = """Error: Invalid DO input"""
        self.inputMsglabel = tk.Label(master, text = self.inputMsgErr, fg = 'red', font = ('helvetica', 12, 'bold'))

        self.loggersDoneLabel = tk.Label(master, text = "All loggers successfully calibrated! Please close this window", fg = 'green', font = ('helvetica', 12, 'bold'))
        
        self.loggerLabel = Label(master, textvariable=self.currentLoggerLabel, font = ('helvetica', 12, 'bold'))
        self.loggerLabel.place(relx = 0.2, rely = 0.8)

        self.listBox = tk.Listbox(master, width=50, height=20)
        for file in self.getFiles():
            self.listBox.insert(tk.END, ntpath.basename(file))
        self.listBox.place(relx = 0.7, rely = 0.1)

        self.pre = tk.IntVar()
        self.rdioOnePre = tk.Radiobutton(master, text='mg/l', variable=self.pre, value=1) 
        self.rdioOnePre.place(relx = 0.55, rely = 0.1)
        self.rdioTwoPre = tk.Radiobutton(master, text='ml/l', variable=self.pre, value=2) 
        self.rdioTwoPre.place(relx = 0.55, rely = 0.15)
        self.rdioThreePre = tk.Radiobutton(master, text='mmol/ml', variable=self.pre, value=3)
        self.rdioThreePre.place(relx = 0.55, rely = 0.2)
        self.unitsLabelPre = tk.Label(master, fg="black", text="Pre-delpoy DO Units", font =('helvetica', 10,'bold') )
        self.unitsLabelPre.place(relx = 0.55, rely = 0.05)
        self.pre.set(1) # initialize

        self.post = tk.IntVar()
        self.rdioOnePost = tk.Radiobutton(master, text='mg/l', variable=self.post, value=1) 
        self.rdioOnePost.place(relx = 0.55, rely = 0.37)
        self.rdioTwoPost = tk.Radiobutton(master, text='ml/l', variable=self.post, value=2) 
        self.rdioTwoPost.place(relx = 0.55, rely = 0.42)
        self.rdioThreePost = tk.Radiobutton(master, text='mmol/ml', variable=self.post, value=3)
        self.rdioThreePost.place(relx = 0.55, rely = 0.47)
        self.unitsLabelPost = tk.Label(master, fg="black", text="Post-deploy DO Units", font =('helvetica', 10,'bold') )
        self.unitsLabelPost.place(relx = 0.55, rely = 0.32)
        self.post.set(1) # initialize

        self.listBoxLabel = tk.Label(master, fg = "black", text = "Files to be Processed", font =('helvetica', 12, 'bold') )
        self.listBoxLabel.place(relx = 0.7, rely = 0.05)

        self.preCsvLabel = tk.Label(master, fg="red", text="No file selected.", font =('helvetica', 12) )  
        self.preCsvLabel.place(relx = 0.08, rely = 0.2) 
        self.browseButton_preCsv = tk.Button(master,text="      Select pre-deployment cal file     ", command=self.getPreCsv, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.browseButton_preCsv.place(relx = 0.08, rely = 0.1)

        self.preEntryTimeLabel = tk.Label(master, text = "Input Time", fg = 'black',font=('helvetica', 12, 'bold'))
        self.preEntryTimeLabel.place(relx = 0.35, rely = 0.05)

        self.preEntryTimeLabel.place(relx = 0.35, rely = 0.05)
        
        self.preEntryTimeOne = tk.Entry(master)
        self.preEntryTimeOne.place(relx = 0.35, rely = 0.1)

        self.preEntryTimeTwo = tk.Entry(master)
        self.preEntryTimeTwo.place(relx = 0.35, rely = 0.15)

        self.preEntryTimeThree = tk.Entry(master)
        self.preEntryTimeThree.place(relx = 0.35, rely = 0.2)

        self.preEntryValueLabel = tk.Label(master, text = "Input Value", fg = 'black',font=('helvetica', 12, 'bold'))
        self.preEntryValueLabel.place(relx = 0.45, rely = 0.05)

        self.preEntryValueOne = tk.Entry(master)
        self.preEntryValueOne.place(relx = 0.45, rely = 0.1)

        self.preEntryValueTwo = tk.Entry(master)
        self.preEntryValueTwo.place(relx = 0.45, rely = 0.15)

        self.preEntryValueThree = tk.Entry(master)
        self.preEntryValueThree.place(relx = 0.45, rely = 0.2)
          
        self.postCsvLabel = tk.Label(master, fg="red", text="No file selected.", font =('helvetica', 12)) 
        self.postCsvLabel.place(relx = 0.08, rely = 0.48)
        self.browseButton_postCsv = tk.Button(master,text="     Select post-deployment cal file     ", command=self.getPostCsv, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.browseButton_postCsv.place(relx = 0.08, rely = 0.37)

        self.postEntryTimeLabel = tk.Label(master, text = "Input Time", fg = 'black',font=('helvetica', 12, 'bold'))
        self.postEntryTimeLabel.place(relx = 0.35, rely = 0.32)

        self.postEntryTimeOne = tk.Entry(master)
        self.postEntryTimeOne.place(relx = 0.35, rely = 0.37)

        self.postEntryTimeTwo = tk.Entry(master)
        self.postEntryTimeTwo.place(relx = 0.35, rely = 0.42)

        self.postEntryTimeThree = tk.Entry(master)
        self.postEntryTimeThree.place(relx = 0.35, rely = 0.47)

        self.postEntryValueLabel = tk.Label(master, text = "Input Value", fg = 'black',font=('helvetica', 12, 'bold'))
        self.postEntryValueLabel.place(relx = 0.45, rely = 0.32)

        self.postEntryValueOne = tk.Entry(master)
        self.postEntryValueOne.place(relx = 0.45, rely = 0.37)

        self.postEntryValueTwo = tk.Entry(master)
        self.postEntryValueTwo.place(relx = 0.45, rely = 0.42)

        self.postEntryValueThree = tk.Entry(master)
        self.postEntryValueThree.place(relx = 0.45, rely = 0.47)

        self.skipButton = tk.Button(master, text = "Skip Logger", command = self.skipButtonCallBack, bg = 'black', fg='white', font=('helvetica', 12, 'bold'), padx = 18, pady = 18)
        self.skipButton.place(relx = 0.7, rely = 0.85)
        
        self.calButton = tk.Button(master,text="Calibrate!", command=self.calButtonCallBack, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'), padx = 25, pady = 25)
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

    def getPreCsv(self): # csv file of pre deployment calibration
        global df_pre
        import_file_path = r"C:\Users\lstol\OneDrive\Documents\Oregon State\Research\DDH\Calibration Files\Pre deployment\4-17-20\2002008_cal_DissolvedOxygen.csv" # testing
        # import_file_path = filedialog.askopenfilename()
        if import_file_path == "":
            pass
        else:
            self.preCsvLabel.config(text=ntpath.basename(import_file_path), fg = "black", font =('helvetica', 12))
            df_pre = pd.read_csv(import_file_path)
            df_pre['ISO 8601 Time'] = pd.to_datetime(df_pre['ISO 8601 Time'])
            print(df_pre)
    
    def getPostCsv(self): # csv file of post deployment calibration
        global df_post
        import_file_path = r"C:\Users\lstol\OneDrive\Documents\Oregon State\Research\DDH\Calibration Files\Post deployment\8-14-20\04-ee-03-73-87-73\2002007_sxt-2020Aug14_155246_DissolvedOxygen.csv" # testing
        # import_file_path = filedialog.askopenfilename()
        if import_file_path == "":
            pass
        else:
            self.postCsvLabel.config(text=ntpath.basename(import_file_path), fg = "black", font =('helvetica', 12))
            df_post = pd.read_csv (import_file_path)
            df_post['ISO 8601 Time'] = pd.to_datetime(df_post['ISO 8601 Time'])
            print (df_post)

    def getLoggerNumber(self): # prints the logger that is currently being calibrated
        loggers = []
        loggerNumber = []
        for path, subdirs, files in os.walk(dataSource):
            for file in files:

                if file.endswith(".csv"):
                    loggers.append(file[:7])
                    loggerNumber = list(set(loggers))      
        
        return loggerNumber
    
    def cycleLoggerText(self): # cycles which logger name is being displayed
        if calCoef is None:
            pass
        else:
            try:
                self.currentLoggerIndex += 1
                #self.currentLoggerIndex %= len(self.LOGGER_TEXT) # wrap around
                self.currentLoggerLabel.set(self.LOGGER_TEXT[self.currentLoggerIndex])
                    
            except IndexError:
                self.loggerLabel.place_forget()
                self.snLabel.place_forget() 
                self.loggersDoneLabel.place(relx = 0.1, rely = 0.8)
          

    def calDataFiles(self): # Queues all the files that are present in the data source that match the logger number that are being displayed
        global calCoef
        loggerValue = self.currentLoggerLabel.get()
        calCoef = self.calcLinearReg()            ## testing, unvover to use
        with open(r'calibration_parms.csv', 'a', newline='') as csvfile:
            fieldnames = ["logger_sn","pre_slope","pre_intcpt", "post_slope","post_intcpt",
            "pre_x1", "pre_x2","pre_x3","preStd_y1","preStd_y2","preStd_y3","post_x1","post_x2",
            "post_x3","postStd_y1","postStd_y2","postStd_y3", "t_pre", "t_post"]
            writer = csv.DictWriter(csvfile, fieldnames= fieldnames)
            writer.writerow({"logger_sn": calCoef[0], "pre_slope": calCoef[1],
            "pre_intcpt": calCoef[2], "post_slope": calCoef[3],"post_intcpt": calCoef[4],
            "pre_x1":calCoef[5], "pre_x2":calCoef[6], "pre_x3":calCoef[7], "preStd_y1":calCoef[8],
            "preStd_y2":calCoef[9], "preStd_y3":calCoef[10], "post_x1":calCoef[11], "post_x2":calCoef[12],
            "post_x3":calCoef[13], "postStd_y1":calCoef[14], "postStd_y2":calCoef[15], "postStd_y3":calCoef[16],
            "t_pre":calCoef[17], "t_post":calCoef[18]})

        for files in os.listdir(dataSource):
            if fnmatch.fnmatch(files, str(loggerValue)+'*'):
                # print(files) 
                self.applyCal(os.path.join(dataSource,files), calCoef)
        if calCoef is None:
            pass
        else:
            self.moveFiles()


    def calcLinearReg(self):
        # self.preEntryTimeOne = "2020-04-17T10:27:03"
        # self.preEntryTimeTwo = "2020-04-17T11:05:03"
        # self.preEntryTimeThree = "2020-04-17T13:30:03"

        # self.preEntryValueOne = 7.87
        # self.preEntryValueTwo = 7.57
        # self.preEntryValueThree = 1.28

        # self.postEntryTimeOne = "2020-08-14T13:12:21"
        # self.postEntryTimeTwo = "2020-08-14T14:02:21"
        # self.postEntryTimeThree = "2020-08-14T15:35:21"

        # self.postEntryValueOne = 8.23
        # self.postEntryValueTwo = 3.05
        # self.postEntryValueThree = 0.01

        try:
            self.timeMsglabel.place_forget()
            self.inputMsglabel.place_forget()
            # idx_t1 = df_pre['ISO 8601 Time'].sub(pd.to_datetime(self.preEntryTimeOne.get())).abs().idxmin()   # Finds closes row to time specified during calibration based on known values
            # idx_t2 = df_pre['ISO 8601 Time'].sub(pd.to_datetime(self.preEntryTimeTwo.get())).abs().idxmin()
            # idx_t3 = df_pre['ISO 8601 Time'].sub(pd.to_datetime(self.preEntryTimeThree.get())).abs().idxmin()

            # idx_t4 = df_post['ISO 8601 Time'].sub(pd.to_datetime(self.postEntryTimeOne.get())).abs().idxmin()
            # idx_t5 = df_post['ISO 8601 Time'].sub(pd.to_datetime(self.postEntryTimeTwo.get())).abs().idxmin()
            # idx_t6 = df_post['ISO 8601 Time'].sub(pd.to_datetime(self.postEntryTimeThree.get())).abs().idxmin()

            idx_t1 = df_pre['ISO 8601 Time'].sub(pd.to_datetime("2020-04-17T10:27:03")).abs().idxmin()   # Finds closes row to time specified during calibration based on known values
            idx_t2 = df_pre['ISO 8601 Time'].sub(pd.to_datetime("2020-04-17T11:05:03")).abs().idxmin()
            idx_t3 = df_pre['ISO 8601 Time'].sub(pd.to_datetime("2020-04-17T13:30:03")).abs().idxmin()

            idx_t4 = df_post['ISO 8601 Time'].sub(pd.to_datetime("2020-08-14T13:12:21")).abs().idxmin()
            idx_t5 = df_post['ISO 8601 Time'].sub(pd.to_datetime("2020-08-14T14:02:21")).abs().idxmin()
            idx_t6 = df_post['ISO 8601 Time'].sub(pd.to_datetime("2020-08-14T15:35:21")).abs().idxmin()

            

            row1 = df_pre.loc[[idx_t1]]
            row2 = df_pre.loc[[idx_t2]] 
            row3 = df_pre.loc[[idx_t3]]

            row4 = df_post.loc[[idx_t4]]
            row5 = df_post.loc[[idx_t5]]
            row6 = df_post.loc[[idx_t6]]

        except Exception: 
            self.timeMsglabel.place(relx = 0.45, rely  = 0.55)
    # except KeyError:
    #     self.timeMsglabel.place(relx = 0.45, rely  = 0.55)

        try:
            self.inputMsglabel.place_forget()
            self.timeMsglabel.place_forget()
            # if self.pre.get() == 1: # mg/l    # testing the linear regression calculation
            #     x_pre = np.array([row1['Dissolved Oxygen (mg/l)'], row2['Dissolved Oxygen (mg/l)'], row3['Dissolved Oxygen (mg/l)']]).reshape((-1,1))  # puts values into two x/y arrays  
            #     y_pre_std = np.array([float(self.preEntryValueOne.get()), float(self.preEntryValueTwo.get()), float(self.preEntryValueThree.get())]).reshape((-1,1))

            if self.pre.get() == 1: # mg/l
                x_pre = np.array([row1['Dissolved Oxygen (mg/l)'], row2['Dissolved Oxygen (mg/l)'], row3['Dissolved Oxygen (mg/l)']]).reshape((-1,1))  # puts values into two x/y arrays  
                y_pre_std = np.array([float(7.87), float(7.57), float(1.28)]).reshape((-1,1))

            elif self.pre.get() == 2: # ml/l
                x_pre = np.array([row1['Dissolved Oxygen (mg/l)'], row2['Dissolved Oxygen (mg/l)'], row3['Dissolved Oxygen (mg/l)']]).reshape((-1,1))  # puts values into two x/y arrays  
                y_pre_std = np.array([self.mll2mgl(float(self.preEntryValueOne.get())), self.mll2mgl(float(self.preEntryValueTwo.get())), self.mll2mgl(float(self.preEntryValueThree.get()))]).reshape((-1,1))

            elif self.pre.get() == 3: # mmol/ml
                x_pre = np.array([row1['Dissolved Oxygen (mg/l)'], row2['Dissolved Oxygen (mg/l)'], row3['Dissolved Oxygen (mg/l)']]).reshape((-1,1))  # puts values into two x/y arrays  
                y_pre_std = np.array([self.mmol2mgl(float(self.preEntryValueOne.get())), self.mmol2mgl(float(self.preEntryValueTwo.get())), self.mmol2mgl(float(self.preEntryValueThree.get()))]).reshape((-1,1))


        except Exception:
            self.inputMsglabel.place(relx = 0.45 , rely = 0.6)
        # except UnboundLocalError:
        #     self.inputMsglabel.place(relx = 0.45 , rely = 0.55)
        
        try: 
            self.inputMsglabel.place_forget()
            self.timeMsglabel.place_forget()
            # if self.post.get() == 1: # mg/l
            #     x_post = np.array([row4['Dissolved Oxygen (mg/l)'], row5['Dissolved Oxygen (mg/l)'], row6['Dissolved Oxygen (mg/l)']]).reshape((-1,1))
            #     y_post_std = np.array([float(self.postEntryValueOne.get()), float(self.postEntryValueTwo.get()), float(self.postEntryValueThree.get())]).reshape((-1,1))

            if self.post.get() == 1: # mg/l
                x_post = np.array([row4['Dissolved Oxygen (mg/l)'], row5['Dissolved Oxygen (mg/l)'], row6['Dissolved Oxygen (mg/l)']]).reshape((-1,1))
                y_post_std = np.array([float(8.23), float(3.05), float(0.01)]).reshape((-1,1))

            elif self.post.get() == 2: # ml/l
                x_post = np.array([row4['Dissolved Oxygen (mg/l)'], row5['Dissolved Oxygen (mg/l)'], row6['Dissolved Oxygen (mg/l)']]).reshape((-1,1))
                y_post_std = np.array([self.mll2mgl(float(self.postEntryValueOne.get())), self.mll2mgl(float(self.postEntryValueTwo.get())), self.mll2mgl(float(self.postEntryValueThree.get()))]).reshape((-1,1))

            elif self.post.get() == 3: # mmol/ml
                x_post = np.array([row4['Dissolved Oxygen (mg/l)'], row5['Dissolved Oxygen (mg/l)'], row6['Dissolved Oxygen (mg/l)']]).reshape((-1,1))
                y_post_std = np.array([self.mmol2mgl(float(self.postEntryValueOne.get())), self.mmol2mgl(float(self.postEntryValueTwo.get())), self.mmol2mgl(float(self.postEntryValueThree.get()))]).reshape((-1,1))

            else:
                pass
        except (ValueError, UnboundLocalError) as error:
            self.inputMsglabel.place(relx = 0.45 , rely = 0.6)
        # except UnboundLocalError:
        #     self.inputMsglabel.place(relx = 0.45 , rely = 0.55)

        try:
            model_pre = LinearRegression().fit(x_pre, y_pre_std) # linear regression to get differences in slope/intercept for pre/post calibrations
            model_post = LinearRegression().fit(x_post,y_post_std)
        except UnboundLocalError:
            self.inputMsglabel.place(relx = 0.45 , rely = 0.6) 

        try:
            # self.inputMsglabel.place_forget()
            # self.timeMsglabel.place_forget()
            # return (self.currentLoggerLabel.get(), float(model_pre.coef_) , float(model_pre.intercept_), 
            # float(model_post.coef_), float(model_post.intercept_), float(x_pre[0]), float(x_pre[1]), float(x_pre[2]), float(y_pre_std[0]),
            # float(y_pre_std[1]), float(y_pre_std[2]), float(x_post[0]), float(x_post[1]), float(x_post[2]), float(y_post_std[0]),
            # float(y_post_std[1]), float(y_post_std[2]),
            # pd.to_datetime(self.preEntryTimeTwo.get()), pd.to_datetime(self.postEntryTimeTwo.get())) 
            return (self.currentLoggerLabel.get(), float(model_pre.coef_) , float(model_pre.intercept_), 
            float(model_post.coef_), float(model_post.intercept_), float(x_pre[0]), float(x_pre[1]), float(x_pre[2]), float(y_pre_std[0]),
            float(y_pre_std[1]), float(y_pre_std[2]), float(x_post[0]), float(x_post[1]), float(x_post[2]), float(y_post_std[0]),
            float(y_post_std[1]), float(y_post_std[2]),
            pd.to_datetime("2020-04-17T11:05:03"), pd.to_datetime("2020-08-14T14:02:21")) 

        except UnboundLocalError:
            pass
            # self.inputMsglabel.place(relx = 0.45 , rely = 0.6)
            # self.timeMsglabel.place(relx = 0.45, rely  = 0.55)


    def applyCal(self, files, coefs):   
        df = pd.read_csv(files)
        df['ISO 8601 Time'] = pd.to_datetime(df['ISO 8601 Time'])


            # writer.writerow({"logger_sn": calCoef[0], "pre_slope": calCoef[1],
            # "pre_intcpt": calCoef[2], "post_slope": calCoef[3],"post_intcpt": calCoef[4],
            # "pre_x1":calCoef[5], "pre_x2":calCoef[6], "pre_x3":calCoef[7], "preStd_y1":calCoef[8],
            # "preStd_y2":calCoef[9], "preStd_y3":calCoef[10], "post_x1":calCoef[11], "post_x2":calCoef[12],
            # "post_x3":calCoef[13], "postStd_y1":calCoef[14], "postStd_y2":calCoef[15], "postStd_y3":calCoef[16],
            # "t_pre":calCoef[17], "t_post":calCoef[18]})

        slope_t = (((coefs[1]*(date2num(coefs[17])-date2num(df['ISO 8601 Time']))))*((coefs[3]-coefs[1])/(date2num(coefs[18])-date2num(coefs[17]))))

        offset_t = ((coefs[2]*(date2num(df['ISO 8601 Time'])-date2num(coefs[17])))*((coefs[4]-coefs[2])/(date2num(coefs[18])-date2num(coefs[17]))))

        print(date2num(coefs[18])-date2num(coefs[17]))
        df['DOcal_mgl'] = slope_t*df['Dissolved Oxygen (mg/l)']+offset_t

        df.to_csv(files, index = False, encoding='utf-8-sig', na_rep = 'NaN')  
        
        # actually apply calibration to calculation
    
    def mmol2mgl(self, mmol):
        mg = mmol/31.1
        return mg
    
    def mll2mgl(self, mml):
        mg = mml/0.7
        return mg

                    
    def moveFiles(self): # moves files after finished cleaning/calibhrating. Then updates the listbox 
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
            self.listBox.insert(tk.END, ntpath.basename(file))
         
    def getFiles(self): # returns all the csv files matching the logger number
        loggerValue = self.currentLoggerLabel.get()
        csvFiles = []
        for path, subdirs, files in os.walk(dataSource):
            for file in files:
                if file.endswith(".csv"):
                    csvFiles.append(file)
        return csvFiles
    
    def calButtonCallBack(self):
        self.calDataFiles()
        self.cycleLoggerText()
    
    def skipButtonCallBack(self):
        self.cycleLoggerText()
        
        
    def clientExit(self):
        exit()


root = Tk()
root.iconbitmap('merman.ico')
root.state('zoomed')

dataSource = r'C:\Users\lstol\Documents\Repositories\FISH-Finder\inbox'  ## Uncover these three to skip the start page
dataDestination = r'C:\Users\lstol\Documents\Repositories\FISH-Finder\outbox'
StartUpScreen = SecondPage(root)

# FishFinder = StartPage(root)

root.mainloop()