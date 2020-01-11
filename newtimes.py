import pandas as pd
from tkinter import *
import tkinter.messagebox

# Creates the newTimes csv file with the given threshold

root = Tk()


def click():
    """ Reads input dataFile and creates new csv with downtime times from the set threshold 550 and set column

        """
    file = csvEntry.get()  # compressor_features_and_failures.csv
    try:
        if file[-4:] == 'xlsx':
            tkinter.messagebox.showinfo('NO XLSX FILES', 'Change your file to a csv file before entering it')
            return
        else:
            df = pd.read_csv(file)
        print('done finding')
    except:
        tkinter.messagebox.showinfo('File not found', 'The data file cannot be found')
        return
    df.set_index('Time', inplace=True)
    df.index = pd.to_datetime(df.index)
    thresh = 550  # can be changed depending on file
    tag = '300PM078.AvgCurrent' # can be changed depending on file
    startTime = df.first_valid_index()
    lastTime = df.last_valid_index()
    StartOfCycle = []
    EndOfCycle = []
    StartOfCycle.append(startTime)
    upTime = True
    startIndex = -1
    endIndex = -2
    while True:
        temp = df.loc[startTime:lastTime]
        if upTime:
            endIndex = temp[temp[tag] <= float(thresh)].first_valid_index()
            temp = df.loc[startTime:endIndex]
            blackCheck = temp[temp[tag] > float(thresh)].last_valid_index()
            if startIndex == endIndex or not endIndex:
                break
            EndOfCycle.append(blackCheck)
            startTime = endIndex
            upTime = False
        else:
            startIndex = temp[temp[tag] > float(thresh)].first_valid_index()
            if startIndex == endIndex or not startIndex:
                break
            StartOfCycle.append(startIndex)
            startTime = startIndex
            upTime = True
    EndOfCycle.append(lastTime)
    print("Start")
    print(StartOfCycle)
    print(len(StartOfCycle))
    print("End")
    print(EndOfCycle)
    print(len(EndOfCycle))
    combined = {'StartTime': StartOfCycle, 'EndTime': EndOfCycle}
    timeDf = pd.DataFrame(combined)
    timeDf.to_csv(r'newTimes.csv')
    root.destroy()


csvFile = Label(root, text='CSV Data File')
csvEntry = Entry(root)
csvFile.pack(side=LEFT)
csvEntry.pack(side=LEFT)
submit = Button(root, text='SUBMIT', width=6, command=click)
submit.pack()


root.mainloop()
