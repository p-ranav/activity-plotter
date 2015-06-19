# Plotting Operating System Scheduler Activity
# Author: Pranav Srinivas Kumar
# Date: 2014.05.16

# Import what?
import csv
from matplotlib.pyplot import *
import matplotlib.transforms as transforms
import matplotlib.pyplot as plt
import pylab
from mpl_toolkits.axes_grid.anchored_artists import AnchoredText

# Global Variables
pid_list = []
tgid_list = []
active_partition_list = []
task_partition_list = []
time_list = []
classifiers = ['idle']
classifier_map = dict()
thread_activity = []
classified_activity = dict()
plot_xticks = []

# Function to parse the classifier file 
def parse_classifier_file(filename):
    row_num = -1
    global classifiers
    print "\nParsing thread classifier file: ", filename
    with open(filename, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            row_num += 1
            if row_num > 0:
                classifiers.append(row[-1])
                if row[-1] in classifier_map:
                    # append the new thread pid to the existing array at this classifier
                    classifier_map[row[-1]].append(int(row[0].replace(',', '')))
                else:
                    # create a new array for this classifier
                    classifier_map[row[-1]] = [int(row[0].replace(',', ''))]

    classified_activity['idle'] = [0]            
    classifiers = list(set(classifiers))
    print "Unique Thread Classifiers: ", list(set(classifiers))
    #print "\nClassifier Map:"
    #print classifier_map
    print "Finished parsing!"

# Function to parse the scheduler log file                
def parse_scheduler_log(filename):
    row_num = -1
    global pid_list, tgid_list, active_partition_list, task_partition_list, time_list
    print "\nParsing ", filename
    with open(filename, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            row_num += 1
            if row_num > 0:
                time_list.append(int(row[4].replace(',', '')))
                thread_activity.append([int(row[0].replace(',', '')), int(row[4].replace(',', ''))])

    #print len(pid_list), len(tgid_list), len(active_partition_list), len(task_partition_list), len(time_list)
    #print thread_activity
    for process, jiffy in thread_activity:
        for classifier, pid_list in classifier_map.iteritems():
            if process in pid_list:
                if classifier in classified_activity:
                    classified_activity[classifier].append(jiffy)
                else:
                    classified_activity[classifier] = [jiffy]

    #print classified_activity
    #print len(time_list)
    print "Finished parsing!"

# Function to plot thread activity - Generates a subplot for each classifier
def plot_activity(filename, plot_start_time, plot_end_time):
    fig = plt.figure()
    subnum = 0
    subplot_count = 0
            
    print "\nPlotting thread activity..."
    for c in classifiers:

        # Identify number of subplots to add
        subset_activity = []
        for subset in classified_activity[c]:
            if subset >= plot_start_time and subset <= plot_end_time:
                subset_activity.append(subset)                
        if subset_activity != []:
            if subnum == 0:
                ax = fig.add_subplot(110)
            if subnum > 0:
                n = len(fig.axes)
                for i in range(n):
                    fig.axes[i].change_geometry(n+1, 1, i+1)
                ax = fig.add_subplot(n+1, 1, n+1)

            # Anchored Text to show plot start time, plot end time and bucket (classifier)
            at = AnchoredText("Plot Start Time:" + str(float(plot_start_time/1000000000.0)) + "s\nPlot End Time: " + str(float(plot_end_time/1000000000.0))+ "s\nBucket: " + str(c),
                  prop=dict(size=10), frameon=True,
                  loc=2,
                  )
            at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
            subnum += 1

        # Accumulate activity in time range and plot
        for activity in classified_activity[c]:
            if activity >= plot_start_time and activity <= plot_end_time:
                #plt.title(c, horizontalalignment = 'left')
                plt.xlabel("Time (s)", horizontalalignment = 'right')
                #plt.ylabel("Thread State")
                plot_x = [float(activity/1000000000.0), float(activity/1000000000.0), float(activity/1000000000.0), float(activity/1000000000.0)]
                plot_y = [0,1,1,0]
                plt.plot(plot_x, plot_y, '-k')
                plt.axis([float(plot_start_time/1000000000.0), float(plot_end_time/1000000000.0), 0, 1.2])
                ax.add_artist(at)

    # Once number of subplots is identified, resize the figure to remove empty space.
    F = pylab.gcf()
    Size = F.get_size_inches()
    F.set_size_inches(20, 3*subnum)
    fig.subplots_adjust(hspace=.5)
    plt.savefig(filename)
    print "Finished Plotting!\n"

# Main Function
if __name__ == "__main__":

    scheduler_log_name = ""
    classifier_file_name = ""
    plot_file_name = ""
    plot_start_time = -1
    plot_end_time = -1

    # Parse config file for Plot Parameters
    f = open('config.txt', 'rb')
    print "Configuration_File: config.txt"
    for line in f:
        #print line
        config_param = line.split(' = ')
        if len(config_param) > 1:
            config_param[1] = config_param[1].strip()
        else:
            config_param[0] = config_param[0].strip()

        if config_param[0] == "Scheduler_Log_Name":
            scheduler_log_name = config_param[1]
            print "Scheduler_Log_File: ", scheduler_log_name
        elif config_param[0] == "Thread_Classifier_File":
            classifier_file_name = config_param[1]
            print "Thread_Classifier_File: ", classifier_file_name
        elif config_param[0] == "Plot_File_Name":
            plot_file_name = config_param[1]
            print "Plot_File_Name: ", plot_file_name
        elif config_param[0] == "Plot_Start_Time":
            plot_start_time = int(config_param[1])
            print "Plot_Start_time: ", plot_start_time
        elif config_param[0] == "Plot_End_Time":
            plot_end_time = int(config_param[1])
            print "Plot_Start_time: ", plot_end_time
            
    # Parse the thread classifier file
    if classifier_file_name == "":
        print "ERROR: No Thread Classifier File found!"
    else:
        parse_classifier_file(classifier_file_name)    

    # Parse the scheduler log file
    if scheduler_log_name == "":
        print "ERROR: No Scheduler Log found!"
    else:
        parse_scheduler_log(scheduler_log_name)

    # Generate plot!
    if plot_start_time == -1:
        print "ERROR: Invalid plot_start_time"
    if plot_end_time == -1:
        print "ERROR: Invalid plot_end_time"
    # From plot_start_time to plot_end_time
    FACE_plot = plt.figure("Thread Activity Plot")
    plot_activity(plot_file_name, plot_start_time, plot_end_time)
 
