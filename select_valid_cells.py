import os
import numpy
import re

#this script is for selecting valid cells from events file and then combining the behavior data with event data

#for PC, the format is something like: directory_path ='C:/Users/axel/Desktop/test_data'
directory_path ='/Users/njoshi/Desktop/events_test'

def extract_details_per_frame (behavior_file, events_file,valid_cells_file):

    behavior = numpy.loadtxt(behavior_file, dtype='int', comments='#', delimiter=',')
    print "Behavior array size is: "
    print behavior.shape
    number_of_frames = behavior.shape[0]
    print 'Total number of frames recorded by arduino: %d'%number_of_frames

    valid_cells = numpy.loadtxt(valid_cells_file, dtype='int', comments='#', delimiter=',')
    print "Valid cell list size is: %d"%valid_cells.size
    number_of_valid_cells = numpy.sum(valid_cells) 
    print "Number of valid cells in this recording: %d"%number_of_valid_cells
    
    
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

    #now save an array with only valid cells
    valid_cell_events = []
    for cell in range(0,len(events)):
        if(valid_cells[cell] == 1):
            valid_cell_events.append(events[cell])
    print 'Size of valid cell events file is: %d'%len(valid_cell_events)    
    print valid_cell_events[0:3]    
    #print valid_cell_events[len(valid_cell_events)-6:len(valid_cell_events)]
    
    
    events_by_frame = numpy.empty((number_of_frames,number_of_valid_cells))   
    
    for this_cell in range(0,number_of_valid_cells):
        frames_in_this_cell = len(valid_cell_events[this_cell])
        for this_frame in range(0,frames_in_this_cell):
            event_frame_index = valid_cell_events[this_cell][this_frame] - 1
            events_by_frame[event_frame_index][this_cell] = 1
    
    
    #now save the array as a csv file in the same location as the input file
    numpy.savetxt(behavior_file.replace('.csv','_combined_behavior_and_events.csv'), events_by_frame, fmt='%i', delimiter=',', newline='\n')

#    for frame in range (0,number_of_frames):
#        for column in range
    
    
  
#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

file_names = [os.path.join(directory_path, f)
    for dirpath, dirnames, files in os.walk(directory_path)
    for f in files if f.endswith('.csv')]
file_names.sort(key=natural_key)

# if there are missing frames, run this statement
if (len(file_names) == 3):
    print 'Behavior file: '+ file_names[0]
    print 'Events file: '+ file_names[1]
    print 'Valid cells: '+ file_names[2]
    extract_details_per_frame(file_names[0],file_names[1],file_names[2])
else:
    print "Please make sure that there are an appropriate number of files in the folder"