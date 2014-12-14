import os
import numpy
import re

#this script is for selecting valid cells from events file and then combining the behavior data with event data

#for PC, the format is something like: directory_path ='C:/Users/axel/Desktop/test_data'
directory_path ='/Users/njoshi/Desktop/events_test'

def extract_details_per_frame (raw_behavior_file, events_file, valid_cells_file, missing_frame_file):
    #fast_output_array = numpy.loadtxt(complete_file, dtype='int', comments='#', delimiter=',', converters=None, skiprows=2, usecols=(0,1,3,5,6,12,15), unpack=False, ndmin=0) 
    
    raw_behavior = numpy.loadtxt(raw_behavior_file, dtype='int', comments='#', delimiter=',', skiprows=2)
    #extract only the relevant columns from the raw behavior file
    behavior = numpy.empty((raw_behavior[len(raw_behavior) - 1][13],8))
    i = -1
    
    for row in range(0, len(raw_behavior)):
        #save data only if there's a new frame in the current data reading
        if(raw_behavior[row][12] > 0):
            i = i + 1
            behavior[i][0] = raw_behavior[row][12]   #frame count
            behavior[i][1] = raw_behavior[row][0]    #time
            behavior[i][2] = raw_behavior[row][1]    #odor
            behavior[i][3] = raw_behavior[row][3]    #lick count
            behavior[i][4] = raw_behavior[row][5]    #reward count
            behavior[i][5] = raw_behavior[row][6]    #distance
            behavior[i][6] = raw_behavior[row][15]   #lap count
            if(raw_behavior.shape[1]>=17):               #environment
                behavior[i][7] = raw_behavior[row][16]   
            else:
                behavior[i][7] = 1
    
    print "Behavior array size is: "
    print behavior.shape
    number_of_frames = behavior.shape[0]
    print 'Total number of frames recorded by arduino: %d'%number_of_frames
###############################################################################


    valid_cells = numpy.loadtxt(valid_cells_file, dtype='int', comments='#', delimiter=',')
    print "Valid cell list size is: %d"%valid_cells.size
    number_of_valid_cells = numpy.sum(valid_cells) 
    print "Number of valid cells in this recording: %d"%number_of_valid_cells   
###############################################################################

    
    #Source: http://stackoverflow.com/questions/4974290/reading-non-uniform-data-from-file-into-array-with-numpy
    f = open(events_file, "r")
    events = []
    line = f.readline()
    index = 0
    while line:
        line = line.strip("\n")
        line = line.split()
        events.append([])
        for item in line:
            events[index].append(int(item))
        line = f.readline()
        index += 1
    f.close()
    print 'Size of events file is: %d'%len(events)    
    print events[0:10]
###############################################################################


    # run this only if there are missing frames
    missing_frames = []
    if (missing_frame_file == 0):
        missing_frames = [0]
        print 'There are no dropped frames in this recording.'
    else:
        missing_frames = numpy.loadtxt(missing_frame_file, dtype='int', comments='#', delimiter=',')
        print "Number of dropped frames: %d"%missing_frames.size
###############################################################################


    #create an array of array with only valid cells
    valid_cell_events = []
    for cell in range(0,len(events)):
        if(valid_cells[cell] == 1):
            valid_cell_events.append(events[cell])
    print 'Size of valid cell events file is: %d'%len(valid_cell_events)    
    print valid_cell_events[0:3]    
    #print valid_cell_events[len(valid_cell_events)-6:len(valid_cell_events)]
    
    #    
    events_by_frame = numpy.empty((number_of_frames,number_of_valid_cells))   
    
    for this_cell in range(0,number_of_valid_cells):
        frames_in_this_cell = len(valid_cell_events[this_cell])
        for this_frame in range(0,frames_in_this_cell):
            event_frame_index = valid_cell_events[this_cell][this_frame] -1
            events_by_frame[event_frame_index][this_cell] = 1
###############################################################################    


    events_adjusted_for_missing_frames = numpy.empty((number_of_frames,behavior.shape[1] + number_of_valid_cells))

    adjust_for_missing_frames = 0
    
    for frame in range(0,number_of_frames):
        if(frame+1 in missing_frames):
            adjust_for_missing_frames = adjust_for_missing_frames + 1
            for cell in range(0,events_adjusted_for_missing_frames.shape[1]):
                if (cell < behavior.shape[1]):
                    events_adjusted_for_missing_frames[frame][cell] = behavior[frame][cell]
                else:
                    events_adjusted_for_missing_frames[frame][cell] = numpy.nan
        #business is as usual if frames are not missing:
        else:
            for cell in range(0,events_adjusted_for_missing_frames.shape[1]):
                if (cell < behavior.shape[1]):
                    events_adjusted_for_missing_frames[frame][cell] = behavior[frame][cell]
                else:
                    events_adjusted_for_missing_frames[frame][cell] = events_by_frame[frame - adjust_for_missing_frames][cell-behavior.shape[1]]           
    
    
    #now save the array as a csv file in the same location as the input file
    numpy.savetxt(raw_behavior_file.replace('.csv','_combined_behavior_and_events.csv'), events_adjusted_for_missing_frames, fmt='%i', delimiter=',', newline='\n')

###############################################################################
###############################################################################
###############################################################################

#we need the files to be in the following order for the analysis to run properly:
#1 behavior
#2 events
#3 valid_cells
#4 missing frames

#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

file_names = [os.path.join(directory_path, f)
    for dirpath, dirnames, files in os.walk(directory_path)
    for f in files if f.endswith('.csv')]
file_names.sort(key=natural_key)


#now on to the actual analysis:
if (len(file_names) == 3):
    print 'Looks like no imaging frames were dropped in this recording. Great!'
    print 'Behavior file: '+ file_names[0]
    print 'Events file: '+ file_names[1]
    print 'Valid cells: '+ file_names[2]
    extract_details_per_frame(file_names[0],file_names[1],file_names[2],0)
# if there are missing frames, run this statement
if (len(file_names) == 4):
    print 'Some imaging frames are missing in this recording.'
    print 'Behavior file: '+ file_names[0]
    print 'Events file: '+ file_names[1]
    print 'Valid cells: '+ file_names[2]
    print 'Missing frame file: '+ file_names[3]
    extract_details_per_frame(file_names[0],file_names[1],file_names[2],file_names[3])
else:
    print "Please make sure that there are an appropriate number of files in the folder"