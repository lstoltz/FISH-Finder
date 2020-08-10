import tkinter as tk
from tkinter import Tk, Label, Button, filedialog
import pandas as pd
import process_files as pf


class FishFinder:
    
    def __init__(self,master):
        self.master = master
        master.title("FISH Finder")

        self.currentLoggerLabel = tk.Label(master, textvariable = self.getLogger, fg = 'black', font = ('helvetica', 12))
        self.currentLoggerLabel.place(relx = 0.6, rely = 0.1)

        self.browseButton_preCsv = tk.Button(master,text="      Select pre-deployment cal file     ", command=self.getPreCsv, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.browseButton_preCsv.place(relx = 0.08, rely = 0.1)

        self.browseButton_postCsv = tk.Button(master,text="     Select post-deployment cal file     ", command=self.getPostCsv, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
        self.browseButton_postCsv.place(relx = 0.08, rely = 0.3)

        self.calButton = tk.Button(master,text="     Calibrate!     ", command=self.calDataFiles, bg='#dc4405', fg='white', font=('helvetica', 12, 'bold'))
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
    # for all loggers of getLoggerNumber() apply data cleaning then calibration factor
        pass

    def getLogger(self):
        print(2002503)

    def client_exit(self):
        exit()

root = Tk()
root.geometry("850x500")
CalibrationProgram = FishFinder(root)

root.mainloop()

# Use this as a template for pre/post deployment calibrations