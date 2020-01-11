import pandas as pd
from tkinter import *
import tkinter.messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.backends.backend_tkagg as tkagg

root = Tk()
fileLabel = Label(root, text='Data file')
fileLabel.grid(row=0, sticky=E)
entry_1 = Entry(root)
entry_1.grid(row=0, column=1)
tagLabel = Label(root, text='Tags file')
tagLabel.grid(row=1, sticky=E)
entry_2 = Entry(root)
entry_2.grid(row=1, column=1)
BottomFrame = Frame(root)
CanvasFrame = Frame(root)


def read():
    """ Takes the Index Plot input and goes to that number maintenance cycle

       """
    global downtime_idx, indexVar
    if not (indexVar.get()).isnumeric():
        tkinter.messagebox.showinfo('Wrong input', 'You must input a number into the Index plot')
        return
    downtime_idx = int(indexVar.get())
    plot()


def decrease():
    """ Goes to the previous maintenance cycle, stops at 0

       """
    global downtime_idx
    downtime_idx -= 1
    plot()


def increase():
    """ Goes to the next maintenance cycle, stops at the last cycle

        """
    global downtime_idx
    downtime_idx += 1
    plot()


def plot():
    """ Plots the current maintenance cycle, with the columns from the dropdown and plots
        when the graph goes below the given threshold

        """
    global col_entry_str_list, root, downtime_idx, EndOfCycle, StartOfCycle, num_col_entries, df, canvas\
        , axis_list, index_number, indexVar, dt, both, tag, thresh
    if downtime_idx < 0:
        downtime_idx = 0
    if downtime_idx >= len(StartOfCycle):
        downtime_idx = len(StartOfCycle) - 1
    print('downtime index is ' + str(downtime_idx))
    print('Length of End Cycle: ' + str(len(EndOfCycle)))
    print('Length of Start Cycle: ' + str(len(StartOfCycle)))
    features_list = []
    for col_entry_idx in range(num_col_entries):
        features_list.append(col_entry_str_list[col_entry_idx].get())
    start = StartOfCycle[downtime_idx]
    end = EndOfCycle[downtime_idx]
    if both is True and downtime_idx + 1 < len(StartOfCycle):
        startNext = StartOfCycle[downtime_idx+1]
    elif both:
        startNext = df.last_valid_index()
    else:
        startNext = None
    for idx in range(num_col_entries):
        plot_df = df.copy()

        col_name = col_entry_str_list[idx].get()
        tag_to_plot = tags_dict[col_name]
        plot_features_list = [tag_to_plot]
        axis_list[idx].clear()
        axis_list[idx].set_title(col_name, fontsize=8)
        axis_list[idx].tick_params(axis='both', labelsize=6)
        axis_list[idx].xaxis.set_label_text('')
        axis_list[idx].set_xlabel('', fontsize=5)

        """std_multiplier = 1.3
        mean = df[tag_to_plot].mean()
        std = df[tag_to_plot].std()
        lower = mean - std_multiplier * std
        upper = mean + std_multiplier * std
        axis_list[idx].set_ylim([lower, upper])
        plot_df = df.loc[start: end].copy()
            plot_df[abs(plot_df[tag_to_plot] - mean) > (1.5 * std)] = None"""
        if both:
            plot_df.loc[start: startNext, plot_features_list].plot(ax=axis_list[idx],
                                                                   fontsize=10, style=(['k-']))
            plot_df.loc[start: end, plot_features_list].plot(ax=axis_list[idx], fontsize=10, style=(['r-']))
            tempStart = start
            temp = df.loc[tempStart:startNext]
            secondLast = temp.index[-2]
            while True:
                underThresh = temp[temp[tag] <= float(thresh)].first_valid_index()
                if not underThresh:
                    break
                temp = df.loc[underThresh:startNext]
                overThresh = temp[temp[tag] > float(thresh)].first_valid_index()
                temp = df.loc[underThresh:overThresh]
                blackCheck = temp[temp[tag] <= float(thresh)].last_valid_index()
                if not overThresh:
                    plot_df.loc[underThresh:startNext, plot_features_list].plot(ax=axis_list[idx], fontsize=10,
                                                                                style=(['b-']))
                    break
                plot_df.loc[underThresh:blackCheck, plot_features_list].plot(ax=axis_list[idx], fontsize=10,
                                                                             style=(['b-']))
                tempStart = overThresh
                temp = df.loc[tempStart:startNext]
            if float(df.loc[startNext, tag]) > float(thresh):
                plot_df.loc[secondLast: startNext, plot_features_list].plot(ax=axis_list[idx], fontsize=10,
                                                                            style=(['k-']))
            axis_list[idx].set_xlim([start, startNext])
            axis_list[idx].tick_params(labelsize=7, which='both')
            axis_list[idx].legend(labels=
                                  ['Start of one given cycle to start of the next',
                                   'Start of one given cycle to end of given cycle',
                                   'downtime for threshold: ' + str(thresh)],
                                  prop={'size': 5})
            if downtime_idx < len(StartOfCycle):
                print('Axis Start and Start : ' + str(start))
                print('End: ' + str(end))
                print('Axis End: ' + str(startNext))
        else:
            plot_df.loc[start: end, plot_features_list].plot(ax=axis_list[idx],
                                                             legend=None,
                                                             style=(['b-']))
            print('Start: ' + str(start))
            print('End: ' + str(end))

    indexVar.set(str(downtime_idx))
    canvas.draw()
    plt.close('all')


def create_dropdown(num_dropdown, columns):
    """ Creates dropdowns

        Args:
            num_dropdown: number of dropdowns to be made (3)
            columns: list of columns from the Tag List file (readable names columns)

        Returns:
            List of StringVars of the default columns shown on the dropdown menu
            (gotten with dropdown_str_list[x].get())
        """
    global root, button_highlight_color
    dropdown_str_list = []
    dropdown_list = []
    for i in range(num_dropdown):
        dropdown_str_list.append(StringVar(root))
        dropdown_str_list[i].set(columns[0])
        dropdown_list.append(OptionMenu(root, dropdown_str_list[i],
                                        *columns))
        dropdown_list[i].config(bg=button_highlight_color, width=30)
        dropdown_list[i].grid(row=0, column=i)
    return dropdown_str_list


def maintenance_cycle():
    """ If only input is threshold and column name, calculates downtime times and thus maintenance cycle times
            with the given threshold

        If only Downtime File is given, gets the given downtime times from the Downtime file

        If both are given, just gets the given downtime times from the Downtime file and calculates the
            threshold times in the plot() function
        """
    global columns_list, df, tags_dict, tagList, col_entry_str_list, root, downtime_idx, EndOfCycle, StartOfCycle, \
        num_col_entries, canvas, axis_list, dt, both, tag, thresh
    both = False
    tag = columnEntry.get()
    thresh = thresholdEntry.get()
    dtFile = DownTimeEntry.get()
    print(tag + " <= " + thresh)
    if thresh == "" and dtFile == "":
        tkinter.messagebox.showinfo('Input Required',
                                    'Either the DownTime File or the Threshold and Column must be an input, or both')
        return
    elif thresh != "" and dtFile == "":
        if not thresh.isnumeric():
            tkinter.messagebox.showinfo('Incorrect Threshold Type', 'The Threshold must be a number')
            return
        if tag not in columns_list:
            tkinter.messagebox.showinfo('Column not found', 'This column is not in the data file')
            return
        if tagList:
            tag = tags_dict[tag]
        print(tag)
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
                if startIndex == endIndex or not endIndex:
                    break
                startTime = endIndex
                upTime = False
            else:
                startIndex = temp[temp[tag] > float(thresh)].first_valid_index()
                if startIndex == endIndex or not startIndex:
                    break
                EndOfCycle.append(startIndex)
                StartOfCycle.append(startIndex)
                startTime = startIndex
                upTime = True
        EndOfCycle.append(lastTime)
        print("Start: ")
        print(StartOfCycle)
        print("End")
        print(EndOfCycle)
    elif thresh == "" and dtFile != "":
        try:
            if dtFile[-4:] == 'xlsx':
                dt = pd.read_excel(dtFile)
            else:
                dt = pd.read_csv(dtFile)
            print('DownTimes File Found!')
        except:
            tkinter.messagebox.showinfo('DownTime', 'The DownTime File cannot be found')
            return
        # StartOfCycle.append(startTime)    If not given initial start time with given times
        StartOfCycle = dt['StartTime'].tolist()
        EndOfCycle = dt['EndTime'].tolist()
        # EndOfCycle.append(lastTime) If not given final end time with given times
    else:
        both = True
        if not thresh.isnumeric():
            tkinter.messagebox.showinfo('Incorrect Threshold Type', 'The Threshold must be a number')
            return
        try:
            if dtFile[-4:] == 'xlsx':
                dt = pd.read_excel(dtFile)
            else:
                dt = pd.read_csv(dtFile)
            print('DownTimes File Found!')
        except:
            tkinter.messagebox.showinfo('DownTime', 'The DownTime File cannot be found')
            return
        dt['StartTime'] = pd.to_datetime(dt['StartTime'])
        dt['EndTime'] = pd.to_datetime(dt['EndTime'])
        print(dt.dtypes)
        StartOfCycle = dt['StartTime'].tolist()
        EndOfCycle = dt['EndTime'].tolist()
        if tag not in columns_list:
            tkinter.messagebox.showinfo('Column not found', 'This column is not in the data file')
            return
        if tagList:
            tag = tags_dict[tag]
    columnname.destroy()
    columnEntry.destroy()
    threshold.destroy()
    thresholdEntry.destroy()
    DownTimeEntry.destroy()
    DownTimeLabel.destroy()
    submit2.destroy()
    num_col_entries = 3
    col_entry_str_list = create_dropdown(num_col_entries, columns_list)

    fig = Figure()
    fig.suptitle("Feature Downtime Plots ylim shifted", fontsize=10)
    fig.subplots_adjust(hspace=0.8)

    axis_list = []
    axis_base = 311

    for idx in range(num_col_entries):
        axis_list.append(fig.add_subplot(axis_base + idx))

    downtime_idx = 0
    CanvasFrame.grid(row=1, columnspan=3)
    canvas = FigureCanvasTkAgg(fig, master=CanvasFrame)
    canvas.get_tk_widget().pack()
    tkagg.NavigationToolbar2Tk(canvas, CanvasFrame)

    plot()
    BottomFrame.grid(row=2, columnspan=3)
    prevButton.pack(side=LEFT)
    nextButton.pack(side=LEFT)
    plotButton.pack(side=LEFT)
    index_number.pack(side=LEFT)
    indexButton.pack(side=LEFT)


def click():
    """ Reads the dataFile and optional tag File, and sets gui for next set of inputs

        """
    global columns_list, df, tags_dict, tagList, root, downtime_idx
    file = entry_1.get()    # compressor_features_and_failures.csv
    tags = entry_2.get()    # Compressor Tag List.xlsx
    print('1st step done')  # Compressor No.8 Feeder Average current
    try:                    # newTimes.csv
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
    print(df.index.dtype)
    print('Start Time: ' + str(df.index[0]))
    if tags != "":
        tagList = True
        if tags == file:
            tkinter.messagebox.showinfo('Incorrect Files', 'The tags file is the same as the Data file')
            return
        try:
            if tags[-4:] == 'xlsx':
                tf = pd.read_excel(tags)
            else:
                tf = pd.read_csv(tags)
            print('tags file found')
        except:
            tkinter.messagebox.showinfo('File not found', 'The tags file cannot be found')
            return
        tags_dict = {tf.loc[i, 'Description']: tf.loc[i, 'Name']  # Description == Nice Name
                     for i in range(1, len(tf.index))}
        columns_list = list(tags_dict.keys())
        if not all(x in df.columns for x in tags_dict.values()):
            tkinter.messagebox.showinfo('File not correct', 'The tags file does not match the corresponding data file')
            return
    else:
        tagList = False
        columns_list = df.columns

    fileLabel.destroy()
    tagLabel.destroy()
    submit.destroy()
    entry_1.destroy()
    entry_2.destroy()
    columnname.grid(row=0, sticky=E)
    columnEntry.grid(row=0, column=1)
    threshold.grid(row=1, sticky=E)
    thresholdEntry.grid(row=1, column=1)
    DownTimeLabel.grid(row=0, column=2, sticky=E)
    DownTimeEntry.grid(row=0, column=3)
    submit2.grid(row=4)


submit = Button(root, text='SUBMIT', width=6, command=click)
submit.grid(row=2)

columnname = Label(root, text='Column Name')
columnEntry = Entry(root)
threshold = Label(root, text='Threshold')
thresholdEntry = Entry(root)
submit2 = Button(root, text='SUBMIT', width=6, command=maintenance_cycle)
button_highlight_color = '#3E4149'
DownTimeLabel = Label(root, text='DownTimes File')
DownTimeEntry = Entry(root)
plotButton = Button(BottomFrame, text='Plot', highlightbackground=button_highlight_color, command=plot)
nextButton = Button(BottomFrame, text='Next >', highlightbackground=button_highlight_color, command=increase)
prevButton = Button(BottomFrame, text='< Prev', highlightbackground=button_highlight_color, command=decrease)
indexButton = Button(BottomFrame, text='Index Plot', highlightbackground=button_highlight_color, command=read)
indexVar = StringVar()
index_number = Entry(BottomFrame, textvariable=indexVar)
downtime_idx = 0

root.mainloop()
