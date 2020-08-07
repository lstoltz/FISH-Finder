import tkinter as tk
from tkinter import filedialog
import pandas as pd
import process_files

root= tk.Tk()
root.title("FISH Finder")
canvas1 = tk.Canvas(root, width = 900, height = 500, bg = 'lightsteelblue2', relief = 'raised')
canvas1.pack()

def getPreCsv():
    global df_pre
    
    import_file_path = filedialog.askopenfilename()
    df_pre = pd.read_csv (import_file_path)
    print (df_pre)

def getPostCsv():
    global df_post

    import_file_path = filedialog.askopenfilename()
    df_post = pd.read_csv (import_file_path)
    print (df_post)
    
browseButton_preCsv = tk.Button(text="      Select pre-deployment cal file     ", command=getPreCsv, bg='green', fg='white', font=('helvetica', 12, 'bold'))
browseButton_postCsv = tk.Button(text="     Select post-deployment cal file     ", command=getPostCsv, bg='green', fg='white', font=('helvetica', 12, 'bold'))
canvas1.create_window(200, 150, window=browseButton_preCsv)
canvas1.create_window(200,300, window=browseButton_postCsv)

root.mainloop()

# Use this as a template for pre/post deployment calibrations