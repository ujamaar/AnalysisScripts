import numpy # needed for various math tasks
import os # needed to find files
import re # needed to arrange filenames alphabetically

#this script is for selecting valid cells from events file and then combining the behavior data with event data

def main():

    imaging_frame_rate = 10 #frequency(frames/sec) at which images were captured by the inscopix scope as the behavior was recording the TTL pulses
    frame_rate_after_down_sampling = 5 #frequency(frames/sec) to which the captured video was down sampled for event analysis    
    frame_ID_adjustment_factor = imaging_frame_rate / frame_rate_after_down_sampling
    print 'Frame adjustment factor for downsampled videos is: %d'%frame_ID_adjustment_factor

    #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><#

    data_files_directory_path ='/Volumes/walter/Virtual_Odor/imaging_data/wfnjC19'
#    data_files_directory_path ='/Users/njoshi/Desktop/data_analysis/input_files'
    
    replace_previous_versions_of_output_files = False
    
    #detect all the behavior.csv files in the folder
    file_names = []
    for dirpath, dirnames, files in os.walk(data_files_directory_path):
        for behavior_file in files:
            if behavior_file.endswith('behavior.csv'):
                if(replace_previous_versions_of_output_files == True):
                    file_names.append(os.path.join(dirpath, behavior_file))
                else:                  
                    behavior_file_has_already_been_analyzed = False
                    for combined_file in files:
                        if combined_file.endswith('combined_behavior_and_traces.csv'):
                            behavior_file_has_already_been_analyzed = True
                            print 'This behavior file has already been combined: ' + behavior_file
                            print 'Delete this combined behavior and traces file:' + combined_file
                    
                    if(behavior_file_has_already_been_analyzed == False):      
                        file_names.append(os.path.join(dirpath, behavior_file))
    # sort the file names to analyze them in a 'natural' alphabetical order
    file_names.sort(key=natural_key)    
    print 'Here are all of the behavior files that will be analyzed now:'
    print file_names
    
    # now look for imaging data for each behavior file and combine all the data into one output file    
    for behavior_file in file_names:  
        # load the events, valid_cells and missing_frames files for the given behavior file
        # first extract the mouse ID and date from behavior file, in order to find the right imaging files
        imaging_files_directory_path,behavior_filename = os.path.split(behavior_file)
        for i in xrange(len(behavior_filename)):
            if(behavior_filename[i] == '_'):
                mouse_ID_and_date = behavior_filename[0:i+11]
                break
        print '----------------------------------------------------------------'
        print '----------------------------------------------------------------'
        print 'Mouse ID is: %s'%mouse_ID_and_date
        print 'Analysing this behavior file: '+ behavior_file
        print 'Imaging files are located at: ' + imaging_files_directory_path
        
        traces_file           = imaging_files_directory_path + '/' + 'traces.csv'
        valid_cells_file      = imaging_files_directory_path + '/' + 'valid_cells.csv' 
        dropped_frames_file   = imaging_files_directory_path + '/' + 'dropped_frames.csv'
        output_file_name      = imaging_files_directory_path + '/' + mouse_ID_and_date

        # This if statement is to make sure that the relevant files are actually there in the folder
        if os.path.isfile(traces_file):        
            print 'The matching traces file is:  '+ traces_file
            if os.path.isfile(valid_cells_file):
                print 'The matching valid_cells file:'+ valid_cells_file
                #if there is a file for dropped frames, print a notification
                if os.path.isfile (dropped_frames_file):
                    print 'This recording has dropped frames: '+ dropped_frames_file
                else: #if there is no file for dropped frames in the imaging folder
                    print 'There were no dropped frames in this recording.'            
                    dropped_frames_file = 0       
                extract_details_per_frame(traces_file,valid_cells_file,behavior_file,dropped_frames_file,frame_ID_adjustment_factor,output_file_name)
        else:
            print ('This behavior file either does not have imaging data, or the imaging files are not named properly. ' +
                   'The script expects to find files with names traces.csv, valid_cells.csv, and dropped_frames.csv (if there are dropped frames)')

    #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><#

#############################################################################################
#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><#
#############################################################################################


#to make sure that the files are processed in the proper order
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def extract_details_per_frame (traces_file, valid_cells_file, raw_behavior_file, dropped_frames_file,frame_ID_adjustment_factor,output_file_name):

    #read the behavior.csv file and load it into a matrix called raw_behavior    
    raw_behavior = numpy.loadtxt(raw_behavior_file, dtype='int', comments='#', delimiter=',',skiprows=2)

    #############################################################################################    
    ############################## code for calculating speed ###################################
    #############################################################################################
    
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
    print 'Minimum speed in this recording: %f' %min_speed 
    print 'Maximum speed in this recording: %f' %max_speed 

    ####################done calculating speed per 50mm stretch of the track#####################

    #############################################################################################    
    ######################### end of code for calculating speed #################################
    #############################################################################################


    #############################################################################################    
    ##################### now combine and save the data in a csv file ###########################
    #############################################################################################

    #use and save only the relevant columns from the raw behavior file
    number_of_frames = max(raw_behavior[:,0])
    behavior = numpy.empty((number_of_frames,12),dtype='int')

    frame_count = 0    
    for row in range(0, len(raw_behavior)):
        #save data only if there's a new frame in the current data reading
        if(raw_behavior[row][0] > frame_count):
            behavior[frame_count][0] = raw_behavior[row][0]    #frame count
            behavior[frame_count][1] = raw_behavior[row][1]    #time
            behavior[frame_count][2] = raw_behavior[row][2]    #odor
            behavior[frame_count][3] = raw_behavior[row][3]    #lick count
            behavior[frame_count][4] = raw_behavior[row][4]    #reward count
            behavior[frame_count][5] = raw_behavior[row][5]    #initial drop count
            behavior[frame_count][6] = raw_behavior[row][6]    #reward window status
            behavior[frame_count][7] = raw_behavior[row][7]    #distance
            behavior[frame_count][8] = raw_behavior[row][8]    #total distance
            behavior[frame_count][9] = raw_behavior[row][9]    #lap count
            behavior[frame_count][10] = raw_behavior[row][10]  #environment
            behavior[frame_count][11] = speed[row]             #speed

            frame_count = raw_behavior[row][0] 

    print "Behavior array size is: "
    print behavior.shape
    print 'Total number of frames recorded by arduino: %d'%number_of_frames

###############################################################################
#apply downsampling to the behavior data
    behavior_frames_downsampled = number_of_frames/frame_ID_adjustment_factor
    behavior_downsampled = numpy.empty((behavior_frames_downsampled,12),dtype='int')

    for frame in xrange(behavior_frames_downsampled):
        behavior_downsampled[frame,:] = behavior[frame*frame_ID_adjustment_factor,:]




###############################################################################


    valid_cells = numpy.loadtxt(valid_cells_file, dtype='int', comments='#', delimiter=',')
    number_of_all_cells = len(valid_cells)
    print "Number of putative cells (valid and invalid): %d"%number_of_all_cells
    
    number_of_valid_cells = 0
    for putative_cell in xrange(number_of_all_cells):
        if(valid_cells[putative_cell] >= 1):
            number_of_valid_cells += 1
    print "Number of valid cells in this recording: %d"%number_of_valid_cells    
 
###############################################################################


    traces_raw_matrix = numpy.loadtxt(traces_file, dtype='float', comments='#', delimiter=',')
    number_of_frames_after_downsampling = traces_raw_matrix.shape[1]
    print 'number of cells:%d'%traces_raw_matrix.shape[0]
    print 'number of frames after downsampling:%d'%number_of_frames_after_downsampling   


    traces_by_frame_for_valid_cells = numpy.empty((number_of_valid_cells,number_of_frames_after_downsampling),dtype='float')    

    cell_index = 0
    for putative_cell in xrange(number_of_all_cells):
        if(valid_cells[putative_cell] >= 1):
            for frame in xrange(number_of_frames_after_downsampling):
                traces_by_frame_for_valid_cells[cell_index,:] = traces_raw_matrix[putative_cell,:]                
            cell_index += 1




#    traces_by_frame_for_valid_cells = numpy.empty((number_of_valid_cells,number_of_frames),dtype='float')    
#
#    cell_index = 0
#    for putative_cell in xrange(number_of_all_cells):
#        if(valid_cells[putative_cell] >= 1):
#            for frame in xrange(number_of_frames_after_downsampling):
#                if(frame*frame_ID_adjustment_factor < number_of_frames):
#                    traces_by_frame_for_valid_cells[cell_index][frame*frame_ID_adjustment_factor] = traces_raw_matrix[putative_cell][frame]
#            if(cell_index < number_of_valid_cells):
#                cell_index += 1



###############################################################################    

    # run this only if there are missing frames
    dropped_frames = []
    if (dropped_frames_file == 0):
        dropped_frames = [0]
        print 'There are no dropped frames in this recording :)'
    else:
        dropped_frames = numpy.loadtxt(dropped_frames_file, dtype='int', comments='#', delimiter=',')
        print "Number of dropped frames: %d"%dropped_frames.size
###############################################################################



    print 'Now we will save all this information in one csv file:'
    #the number of frames will be determined by size of behavior_downsampled and number_of_frames_after_downsampling, whichever is smaller
    traces_adjusted_for_missing_frames = numpy.zeros((min(number_of_frames_after_downsampling,behavior_downsampled.shape[0]),behavior_downsampled.shape[1] + number_of_valid_cells),dtype='float')

    adjust_for_missing_frames = 0
    
    for frame in xrange(traces_adjusted_for_missing_frames.shape[0]):
        if(((frame+1)*frame_ID_adjustment_factor) in dropped_frames):
            adjust_for_missing_frames = adjust_for_missing_frames + 1
            for cell in xrange(traces_adjusted_for_missing_frames.shape[1]):
                if (cell < behavior_downsampled.shape[1]): #fill behavior data in the first 12 columns
                    traces_adjusted_for_missing_frames[frame][cell] = behavior_downsampled[frame][cell]
                else:
                    traces_adjusted_for_missing_frames[frame][cell] = 0 # use numpy.nan to be more exact, b/c the frame is missing
        #business is as usual if frames are not missing:
        else:
            for cell in range(0,traces_adjusted_for_missing_frames.shape[1]):
                if (cell < behavior_downsampled.shape[1]): #fill behavior data in the first 12 columns
                    traces_adjusted_for_missing_frames[frame][cell] = behavior_downsampled[frame][cell]
                else: #fill trace values in the remaining columns
                    traces_adjusted_for_missing_frames[frame][cell] = traces_by_frame_for_valid_cells[cell-behavior_downsampled.shape[1]][frame - adjust_for_missing_frames]   
    
    print 'The saved array size is:'
    print traces_adjusted_for_missing_frames.shape
    #now save the array as a csv file in the same location as the input files
    save_file_name = output_file_name + '_combined_behavior_and_traces.csv'
    #print save_file_name
    numpy.savetxt(save_file_name, traces_adjusted_for_missing_frames, fmt='%1.5f', delimiter=',', newline='\n') 
###############################################################################





#    print 'Now we will save all this information in one csv file:'
#    traces_adjusted_for_missing_frames = numpy.empty((number_of_frames,behavior.shape[1] + number_of_valid_cells),dtype='float')
#
#    adjust_for_missing_frames = 0
#    
#    for frame in xrange(number_of_frames):
#        if(frame+1 in dropped_frames):
#            adjust_for_missing_frames = adjust_for_missing_frames + 1
#            for cell in xrange(traces_adjusted_for_missing_frames.shape[1]):
#                if (cell < behavior.shape[1]):
#                    traces_adjusted_for_missing_frames[frame][cell] = behavior[frame][cell]
#                else:
#                    traces_adjusted_for_missing_frames[frame][cell] = 0 # use numpy.nan to be more exact, b/c the frame is missing
#        #business is as usual if frames are not missing:
#        else:
#            for cell in range(0,traces_adjusted_for_missing_frames.shape[1]):
#                if (cell < behavior.shape[1]):
#                    traces_adjusted_for_missing_frames[frame][cell] = behavior[frame][cell]
#                else:
#                    traces_adjusted_for_missing_frames[frame][cell] = traces_by_frame_for_valid_cells[cell-behavior.shape[1]][frame - adjust_for_missing_frames]   
#    
#    print 'The saved array size is:'
#    print traces_adjusted_for_missing_frames.shape
#    #now save the array as a csv file in the same location as the input files
#    save_file_name = output_file_name + '_combined_behavior_and_traces.csv'
#    print save_file_name
#    numpy.savetxt(save_file_name, traces_adjusted_for_missing_frames, fmt='%1.5f', delimiter=',', newline='\n') 
################################################################################
###############################################################################

main()

