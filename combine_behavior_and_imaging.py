import numpy # needed for various math tasks
import os # needed to arrange filenames alphabetically
import re # needed to arrange filenames alphabetically

#this script is for selecting valid cells from events file and then combining the behavior data with event data

#we need the files to be in the following order for the analysis to run properly:
#1 behavior
#2 events
#3 valid_cells
#4 missing frames

def main():
    #for PC, the format is something like: directory_path ='C:/Users/axel/Desktop/test_data'
    directory_path ='/Users/njoshi/Desktop/events_test'

    #detect all the .csv files in the folder
    file_names = [os.path.join(directory_path, f)
        for dirpath, dirnames, files in os.walk(directory_path)
        for f in files if f.endswith('.csv')]
    file_names.sort(key=natural_key)
    
    imaging_frame_rate = 10 #frequency(frames/sec) at which images were captured by the inscopix scope as the behavior was recording the TTL pulses
    frame_rate_after_down_sampling = 5 #frequency(frames/sec) to which the captured video was down sampled for event analysis
    
    frame_ID_adjustment_factor = imaging_frame_rate / frame_rate_after_down_sampling
    print 'Frame adjustment factor for this recording is: %d'%frame_ID_adjustment_factor

    #now on to the actual analysis:
    if (len(file_names) == 3):
        print 'Looks like no imaging frames were dropped in this recording. Great!'
        print 'Events file: '+ file_names[0]
        print 'Valid cells: '+ file_names[1]
        print 'Behavior file: '+ file_names[2]
        extract_details_per_frame(file_names[0],file_names[1],file_names[2],0,frame_ID_adjustment_factor)
    # if there are missing frames, run this statement
    elif (len(file_names) == 4):
        print 'Some imaging frames are missing in this recording.'
        print 'Events file: '+ file_names[0]
        print 'Valid cells: '+ file_names[1]
        print 'Behavior file: '+ file_names[2]
        print 'Missing frame file: '+ file_names[3]
        extract_details_per_frame(file_names[0],file_names[1],file_names[2],file_names[3],frame_ID_adjustment_factor)
    else:
        print "Please make sure that there are an appropriate number of files in the folder"


#to make sure that the files are processed in the proper order
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def extract_details_per_frame (events_file, valid_cells_file, raw_behavior_file, missing_frame_file,frame_ID_adjustment_factor):
    #fast_output_array = numpy.loadtxt(complete_file, dtype='int', comments='#', delimiter=',', converters=None, skiprows=2, usecols=(0,1,3,5,6,12,15), unpack=False, ndmin=0) 
    
    raw_behavior = numpy.loadtxt(raw_behavior_file, dtype='int', comments='#', delimiter=',',skiprows=2)

    #############################################################################################    
    ############################## code for calculating speed ###################################
    #############################################################################################
    
#    #calculate speed per 50mm stretch of the track########################################
#    s1 = 0.00
#    s2 = 0.00
#    t1 = 0.00
#    t2 = 0.00
#    last_line_fill = 0
#    speed = numpy.zeros(len(raw_behavior),dtype='float')
#
#    
#    current_speed = 0.00
#    #current_lick_rate = 0.0    
#    
#    for line in range(0,len(raw_behavior)):
#        #read current distance and time
#        s2 = raw_behavior[line][7]
#        #sanity_check = raw_behavior[line-1][6]
#        #if there is no change in time, the speed remains unchanged
#        #speed is calculated for every 500 ms window in this case
#        if (s2 >= ((int(s1/50.00) + 1)*50.00)):# and (abs(s2-sanity_check) < 20.00)):
#            t2 = raw_behavior[line-1][1]
#            s2 = raw_behavior[line-1][7]
#            current_speed = ((s2 - s1)*1000.00)/(t2 - t1) #speed is in mm/s
#
#            t1 = raw_behavior[line][1]
#            s1 = raw_behavior[line][7]
#            
#            for blank_line in range(last_line_fill,line):
#                speed[blank_line] = current_speed
#            last_line_fill = line
#        #at the end of reward region, when the distance measurement resets to zero
#        elif(s2 < s1 and s1-s2 > 50.00):
#            t2 = raw_behavior[line-1][1]
#            s2 = raw_behavior[line-1][7]          
#            current_speed = ((s2 - s1)*1000.00)/(t2 - t1) #speed is in mm/s
#            for blank_line in range(last_line_fill,line):
#                speed[blank_line] = current_speed
#            last_line_fill = line            
#            t1 = raw_behavior[line][1]
#            s1 = raw_behavior[line][7]
#        #at the end of the recording
#        elif(line == len(raw_behavior)-1):
#            t2 = raw_behavior[line][1]
#            s2 = raw_behavior[line][7]          
#            current_speed = ((s2 - s1)*1000.00)/(t2 - t1) #speed is in mm/s
#            for blank_line in range(last_line_fill,line+1):
#                speed[blank_line] = current_speed
#            last_line_fill = line            


    #calculate speed per 500ms of the recording time########################################
    s1 = 0.00
    s2 = 0.00
    t1 = 0.00
    t2 = 0.00
    last_line_fill = 0
    speed = numpy.zeros(len(raw_behavior),dtype='int')

    
    current_speed = 0 
    
    for line in range(0,len(raw_behavior)):
        #read current distance and time
        t2 = raw_behavior[line][1]
        s2 = raw_behavior[line][7]
        #sanity_check = raw_behavior[line-1][6]
        #if there is no change in time, the speed remains unchanged
        #speed is calculated for every 500 ms window in this case
        if (t2 - t1 > 500 and abs(s2-s1) < 2000):
            t2 = raw_behavior[line-1][1]
            s2 = raw_behavior[line-1][7]
            current_speed = int(((s2 - s1)*1000.00)/(t2 - t1)) #speed is in mm/s

            t1 = raw_behavior[line][1]
            s1 = raw_behavior[line][7]
            
            for blank_line in range(last_line_fill,line):
                speed[blank_line] = current_speed
            last_line_fill = line
        
        #at the end of reward region, when the distance measurement resets to zero
        elif(abs(s2-s1) > 2000 and t2 - t1 >= 100): #to reset values when a new track starts
            t2 = raw_behavior[line-1][1]
            s2 = raw_behavior[line-1][7]          
            current_speed = int(((s2 - s1)*1000.00)/(t2 - t1)) #speed is in mm/s
            for blank_line in range(last_line_fill,line):
                speed[blank_line] = current_speed
            last_line_fill = line            
            t1 = raw_behavior[line][1]
            s1 = raw_behavior[line][7]
        elif(abs(s2-s1) > 2000 and t2 - t1 < 100): #to reset values when a new track starts         
            current_speed = speed[last_line_fill] #speed is in mm/s
            for blank_line in range(last_line_fill+1,line):
                speed[blank_line] = current_speed
            last_line_fill = line            
            t1 = raw_behavior[line][1]
            s1 = raw_behavior[line][7]

        #at the end of the recording
        elif(line == len(raw_behavior)-1 and t2-t1 > 0):
            current_speed = int(((s2 - s1)*1000.00)/(t2 - t1)) #speed is in mm/s
            for blank_line in range(last_line_fill,line+1):
                speed[blank_line] = current_speed
            
    min_speed = min(speed)
    max_speed = max(speed)
    print 'Minimum speed was: %f' %min_speed 
    print 'Maximum speed was: %f' %max_speed 

    ####################done calculating speed per 50mm stretch of the track#####################

    #############################################################################################    
    ######################### end of code for calculating speed #################################
    #############################################################################################




    #############################################################################################    
    ##################### now combine and save the data in a csv file ###########################
    #############################################################################################

    #use and save only the relevant columns from the raw behavior file
    behavior = numpy.empty((raw_behavior[len(raw_behavior) - 1][0],9),dtype='int')
    frame_count = 0
    
    for row in range(0, len(raw_behavior)):
        #save data only if there's a new frame in the current data reading
        if(raw_behavior[row][0] > frame_count):
            behavior[frame_count][0] = raw_behavior[row][0]    #frame count
            behavior[frame_count][1] = raw_behavior[row][1]    #time
            behavior[frame_count][2] = raw_behavior[row][2]    #odor
            behavior[frame_count][3] = raw_behavior[row][3]    #lick count
            behavior[frame_count][4] = raw_behavior[row][4]    #reward count
#            behavior[frame_count][4] = raw_behavior[row][5]    #initial drop count
#            behavior[frame_count][4] = raw_behavior[row][6]    #reward window status
            behavior[frame_count][5] = raw_behavior[row][7]    #distance
            behavior[frame_count][6] = raw_behavior[row][9]    #
            behavior[frame_count][7] = raw_behavior[row][10]   #lap count
            behavior[frame_count][8] = speed[row]              #speed
            frame_count = raw_behavior[row][0] 
    
    print "Behavior array size is: "
    print behavior.shape
    number_of_frames = behavior.shape[0]
    print 'Total number of frames recorded by arduino: %d'%number_of_frames

    
###############################################################################


    valid_cells = numpy.loadtxt(valid_cells_file, dtype='int', comments='#', delimiter=',')
    print "Number of putative cells: %d"%valid_cells.size
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
    print 'Some events for cells(valid as well as impostors):'
    print events[0:5]
###############################################################################


    #create an array of array with only valid cells
    valid_cell_events = []
    for cell in range(0,len(events)):
        if(valid_cells[cell] == 1):
            valid_cell_events.append(events[cell])
    #print 'Size of valid cell events file is: %d'%len(valid_cell_events)    
    #print valid_cell_events[0:3]    
    #print valid_cell_events[len(valid_cell_events)-6:len(valid_cell_events)]
      
    events_by_frame = numpy.empty((number_of_frames,number_of_valid_cells),dtype='int')   
    max_frame_with_event = 0
    for this_cell in range(0,number_of_valid_cells):
        frames_in_this_cell = len(valid_cell_events[this_cell])
        for this_frame in range(0,frames_in_this_cell):
            event_frame_index = (valid_cell_events[this_cell][this_frame] -1)*frame_ID_adjustment_factor #multiply by the adjustment factor because imaging data has been down sampled (e.g. 10 frames/sec down sampled to 5)
            events_by_frame[event_frame_index][this_cell] = 1
            if(event_frame_index > max_frame_with_event):
                max_frame_with_event = event_frame_index
    print 'The last event was registered at frame# %d'%max_frame_with_event
###############################################################################    


    # run this only if there are missing frames
    missing_frames = []
    if (missing_frame_file == 0):
        missing_frames = [0]
        print 'There are no dropped frames in this recording :)'
    else:
        missing_frames = numpy.loadtxt(missing_frame_file, dtype='int', comments='#', delimiter=',')
        print "Number of dropped frames: %d"%missing_frames.size
###############################################################################

    print 'Now we will nicely pack and save all this information in one csv file:'
    events_adjusted_for_missing_frames = numpy.empty((number_of_frames,behavior.shape[1] + number_of_valid_cells),dtype='int')

    adjust_for_missing_frames = 0
    
    for frame in range(0,number_of_frames):
        if(frame+1 in missing_frames):
            adjust_for_missing_frames = adjust_for_missing_frames + 1
            for cell in range(0,events_adjusted_for_missing_frames.shape[1]):
                if (cell < behavior.shape[1]):
                    events_adjusted_for_missing_frames[frame][cell] = behavior[frame][cell]
                else:
                    events_adjusted_for_missing_frames[frame][cell] = 0 # use numpy.nan to be more exact, b/c the frame is missing
        #business is as usual if frames are not missing:
        else:
            for cell in range(0,events_adjusted_for_missing_frames.shape[1]):
                if (cell < behavior.shape[1]):
                    events_adjusted_for_missing_frames[frame][cell] = behavior[frame][cell]
                else:
                    events_adjusted_for_missing_frames[frame][cell] = events_by_frame[frame - adjust_for_missing_frames][cell-behavior.shape[1]]           
    
    print 'The saved array size is:'
    print events_adjusted_for_missing_frames.shape
    #now save the array as a csv file in the same location as the input file
    #numpy.savetxt(raw_behavior_file.replace('.csv','_and_events.csv'), events_adjusted_for_missing_frames, fmt='%1.3f', delimiter=',', newline='\n')
    save_file_name = raw_behavior_file[0:-16] + '_behavior_and_events.csv'
    print save_file_name
    numpy.savetxt(save_file_name, events_adjusted_for_missing_frames, fmt='%i', delimiter=',', newline='\n')    
    #numpy.savetxt(raw_behavior_file.replace('.csv','_behavior_and_events.csv'), events_adjusted_for_missing_frames, fmt='%i', delimiter=',', newline='\n')
###############################################################################

main()

