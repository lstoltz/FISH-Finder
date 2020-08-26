# FISH-Finder
GUI for complete dissolved oxygen sensor calibration and data cleaning. This GUI works on an "inbox/outbox" system, with input required by the user. 

## Getting Started:
Simply run the python script or exe file and then the program will ask the user to select a folder where data are located, and another folder for the data to be sent upon completion. For best practices, keep a copy of the data being processed with FISH-finder, as the program modifies files in the data source folder.

### Calibration:
After speciifying the source and destination folders, the user can now navigate to the next page in the program by hitting "Next". The next page will show information collected from the data source specified on the previous page. The box on the upper right corner of the program displays all of the CSV files present in the data source folder. The user will then select the pre and post deployment oxygen profile files that were collected for calibration purposes. The user will also input a time and  oxygen value from a standard calibration that was performed concurrently with the data logger for both pre and post deployemnt.

Times can be input in the following formats: 
```python
2020-07-23 14:22:00
2020-07-23T14:22:00.000
```

After all the time and oxygen fields have been filled with the values from the concurrent calibration the user can click the "calibrate!" button. The program will then take the inputted time and oxygen values and search through the pre/post calibration files for the specific logger and perform a series of linear regressions to collect a correction factor that is then applied to all CSV files in the listbox that match the currect logger number. Therefore, make certain that all data files of the same logger number share the same pre/post deployemnt oxygen profile files, i.e. all files are of the same deployemnt.


## Disclaimer:
This program was designed to work with Lowell Instruments Deck Data Hub files. Trying to process files not conforming to this file/folder structure may result in unintended outcomes. Again, do not perform use this program to modify original data files. Make certain that the times inputted actually can be found in the pre/post deployment calibration files else the program will not work. 

### For more information:
If any bugs are noticed, please contact Linus Stoltz at Oregon State University for troubleshooting
