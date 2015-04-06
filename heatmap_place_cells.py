import matplotlib.pyplot as plt # needed for plotting graphs
import numpy # needed for various math tasks
from matplotlib.ticker import MaxNLocator #y-axis labels
from matplotlib.backends.backend_pdf import PdfPages # for saving figures as pdf
import os # needed to arrange filenames alphabetically
import re # needed to arrange filenames alphabetically
from scipy import ndimage # needed to apply gaussian filter


def main():
    # specify the various parameters as needed:
    odor_response_time_window = 2000 #time in ms
    distance_bin_size = 50 #distance bin in mm
    speed_threshold = 50 #minimum speed in mm/s for selecting events
    gaussian_filter_sigma = 2.00
    lower_threshold_for_activity = 0.2
    
    # here use these values:
    #split_laps_in_environment=1  #for no split
    #split_laps_in_environment=5050 #to split the laps into earlier and later half 
    #split_laps_in_environment=1212 #to split into odd and even trials
    split_laps_in_environment = 1

    data_files_directory_path ='/Users/njoshi/Desktop/data_analysis'
    output_directory_path = '/Users/njoshi/Desktop/output_files'

#    data_files_directory_path  = '/Volumes/walter/Virtual_Odor/imaging_data/wfnjC23'
#    output_directory_path = '/Volumes/walter/Virtual_Odor/analysis'

    replace_previous_versions_of_plots = True   

    #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><#

    #detect all the behavior.csv files in the folder
    file_names = []
    for dirpath, dirnames, files in os.walk(data_files_directory_path):
        for behavior_file in files:
            if behavior_file.endswith('combined_behavior_and_events.csv'):                
                if(replace_previous_versions_of_plots == True):
                    file_names.append(os.path.join(dirpath, behavior_file))
                else:
                    # to check if there's already a plot for the given file
                    pdf_name = behavior_file[0:18] + generate_plot_pdf_name(split_laps_in_environment,lower_threshold_for_activity)
                    behavior_file_has_already_been_analyzed = False
                    for plot_dirpath, plot_dirnames, plot_files in os.walk(output_directory_path):
                        for plot_file in plot_files:
                            if (plot_file == pdf_name):
                                behavior_file_has_already_been_analyzed = True
                                print '----------------------------------------------------------------'
                                print 'This behavior file has already been plotted: ' + behavior_file
                                print 'Delete this plot to generate a new version: ' + os.path.join(dirpath, plot_file)            
                    if(behavior_file_has_already_been_analyzed == False):      
                        file_names.append(os.path.join(dirpath, behavior_file))

                
    # sort the file names to analyze them in a 'natural' alphabetical order
    file_names.sort(key=natural_key)    
    print 'Here are all of the behavior files that will be analyzed now:'
    print file_names
    
    # now look for imaging data for each behavior file and combine all the data into one output file    
    for behavior_and_events in file_names:
        print '----------------------------------------------------------------'
        print '----------------------------------------------------------------'
        print 'Plotting this file: '+ behavior_and_events

        #create an output folder for the plots, one folder per mouse 
        # first extract the mouse ID and date from behavior file, to create a folder with the correct name
        mouse_ID_first_letter = 0
        file_length = len(behavior_and_events)
        for name_letter in range (1,file_length):
            if(behavior_and_events[file_length - name_letter] == 'w' or behavior_and_events[file_length - name_letter] == 'W'):
                mouse_ID_first_letter = file_length - name_letter
                break
        mouse_ID = behavior_and_events[mouse_ID_first_letter:(mouse_ID_first_letter+7)]
        mouse_ID_and_date = behavior_and_events[mouse_ID_first_letter:(mouse_ID_first_letter+18)]
        print 'Mouse ID is: %s'%mouse_ID_and_date

        #create create a folder, if it is not already there 
        mouse_directory_path = output_directory_path + '/' + mouse_ID  + '/place_cell_plots'
        if mouse_directory_path:
            if not os.path.isdir(mouse_directory_path):
                os.makedirs(mouse_directory_path) 
        
        plot_name_mouse_ID_and_date = mouse_directory_path + '/' + mouse_ID_and_date
        output_plot_pdf_name = plot_name_mouse_ID_and_date + generate_plot_pdf_name(split_laps_in_environment,lower_threshold_for_activity)
        read_data_and_generate_plots(behavior_and_events,odor_response_time_window, distance_bin_size,speed_threshold,gaussian_filter_sigma,lower_threshold_for_activity,split_laps_in_environment,output_plot_pdf_name)

    #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><#


#############################################################################################
#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><#
#############################################################################################

def generate_plot_pdf_name(split_laps_in_environment,lower_threshold_for_activity):

    pdf_name = '_place_cells_%1.2f.pdf'%lower_threshold_for_activity
       
    if(split_laps_in_environment == 5050):            
        pdf_name = '_place_cells_earlier_vs_later_%1.2f.pdf'%lower_threshold_for_activity 
    elif(split_laps_in_environment == 1212):            
        pdf_name = '_place_cells_odd_vs_even_%1.2f.pdf'%lower_threshold_for_activity    

    return pdf_name

#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]



def split_laps_into_earlier_and_later(old_env_seq,total_number_of_frames, lap_count,laps_in_environment):  
    #################separate the earlier and later trials of each environment equally#################

    new_environment_sequence = numpy.zeros(total_number_of_frames,dtype='int')
        
    env1_half_laps = 0
    env2_half_laps = 0
    
    if (len(laps_in_environment) == 2): #if there are two environments originally
        env1_half_laps = laps_in_environment[0] / 2
        env2_half_laps = laps_in_environment[1] / 2
    elif (len(laps_in_environment) == 1): #if there's only one environment originally
        env1_half_laps = laps_in_environment[0] / 2
        env2_half_laps = 0
    
    env1_lap_count = 0
    env2_lap_count = 0
    
    for frame in range(0,total_number_of_frames-1):
        frame_env = old_env_seq[frame]
        frame_lap = lap_count[frame]
        next_frame_lap = lap_count[frame+1]

        if(frame_lap == next_frame_lap and frame_env == 1 and env1_lap_count < env1_half_laps):
            new_environment_sequence[frame] = 1
        elif(next_frame_lap == frame_lap+1 and frame_env == 1 and env1_lap_count < env1_half_laps):
            new_environment_sequence[frame] = 1
            env1_lap_count = env1_lap_count + 1

        elif(frame_lap == next_frame_lap and frame_env == 1 and env1_lap_count >= env1_half_laps):
            new_environment_sequence[frame] = 2
        elif(next_frame_lap == frame_lap+1 and frame_env == 1 and env1_lap_count >= env1_half_laps):
            new_environment_sequence[frame] = 2
            env1_lap_count = env1_lap_count + 1

        elif(frame_lap == next_frame_lap and frame_env == 2 and env2_lap_count < env2_half_laps):
            new_environment_sequence[frame] = 3
        elif(next_frame_lap == frame_lap+1 and frame_env == 2 and env2_lap_count < env2_half_laps):
            new_environment_sequence[frame] = 3
            env2_lap_count = env2_lap_count + 1

        elif(frame_lap == next_frame_lap and frame_env == 2 and env2_lap_count >= env2_half_laps):
            new_environment_sequence[frame] = 4
        elif(next_frame_lap == frame_lap+1 and frame_env == 2 and env2_lap_count >= env2_half_laps):
            new_environment_sequence[frame] = 4
            env2_lap_count = env2_lap_count + 1
        else:
            new_environment_sequence[frame] = -1  
            print 'There is an unexpected environment value in this file'

    new_environment_sequence[total_number_of_frames -1] = new_environment_sequence[total_number_of_frames -2]
 
    print 'Env 1 total lap count is: %d'%env1_lap_count
    print 'Env 2 total lap count is: %d'%env2_lap_count
    print 'Env 1 first half laps: %d'%env1_half_laps
    print 'Env 2 first half laps: %d'%env2_half_laps   
    return new_environment_sequence
    ############### done separating the earlier and later trials of each environment equally############


def split_laps_into_odd_and_even(old_env_seq,total_number_of_frames, lap_count):       
    #################separate odd and even trials of each environment#################

    new_environment_sequence = numpy.zeros(total_number_of_frames,dtype='int')
    last_env1 = 2
    last_env2 = 4
    for frame in range(0,total_number_of_frames-1):
        frame_env = old_env_seq[frame]
        frame_lap = lap_count[frame]
        next_frame_lap = lap_count[frame+1]

        if(frame_lap == next_frame_lap and frame_env == 1 and last_env1 == 2):
            new_environment_sequence[frame] = 1
        elif(next_frame_lap == frame_lap+1 and frame_env == 1 and last_env1 == 2):
            new_environment_sequence[frame] = 1
            last_env1 = 1

        elif(frame_lap == next_frame_lap and frame_env == 1 and last_env1 == 1):
            new_environment_sequence[frame] = 2
        elif(next_frame_lap == frame_lap+1 and frame_env == 1 and last_env1 == 1):
            new_environment_sequence[frame] = 2
            last_env1 = 2

        elif(frame_lap == next_frame_lap and frame_env == 2 and last_env2 == 4):
            new_environment_sequence[frame] = 3
        elif(next_frame_lap == frame_lap+1 and frame_env == 2 and last_env2 == 4):
            new_environment_sequence[frame] = 3
            last_env2 = 3

        elif(frame_lap == next_frame_lap and frame_env == 2 and last_env2 == 3):
            new_environment_sequence[frame] = 4
        elif(next_frame_lap == frame_lap+1 and frame_env == 2 and last_env2 == 3):
            new_environment_sequence[frame] = 4
            last_env2 = 4
        else:
            new_environment_sequence[frame] = -1
            print 'There is an unexpected environment value in this file'

    new_environment_sequence[total_number_of_frames -1] = new_environment_sequence[total_number_of_frames -2]
    return new_environment_sequence
    ################# done separating odd and even trials of each environment#################



def read_data_and_generate_plots(file_path,odor_response_time_window, distance_bin_size,speed_threshold,gaussian_filter_sigma,lower_threshold_for_activity,split_laps_in_environment,plot_pdf_name):
    
    behavior_and_event_data = numpy.loadtxt(file_path, dtype='int', delimiter=',')
    
    #to plot time as x-axis, transpose the whole array
    behavior_and_event_data = behavior_and_event_data.transpose()
    print 'In this recording:'
    print "Events array size is: (%d ,%d)" %(behavior_and_event_data.shape[0], behavior_and_event_data.shape[1])
    
    #row 0 = frame number
    #row 1 = time
    #row 2 = odor
    #row 3 = licks
    #row 4 = rewards
    #row 5 = initial drops
    #row 6 = reward window
    #row 7 = distance
    #row 8 = total distance
    #row 9 = lap
    #row 10 = environment
    #row 11 = speed
    #row 12 to last row = event data for cells in this recording
    
    #time_stamp = behavior_and_event_data[1,:]

    odor = behavior_and_event_data[2,:]
    lap_count = behavior_and_event_data[9,:]
    total_laps = max(lap_count) + 1
    print 'Number of laps = %d' %total_laps
    
    distance = behavior_and_event_data[7,:] 
    environment = behavior_and_event_data[10,:]
        
    number_of_environments = max(environment)
    print 'Number of environments = %d' %number_of_environments

    
    running_speed = behavior_and_event_data[11,:]
    print 'Maximum speed was: %f' %max(running_speed)    
    print 'Minimum speed was: %f' %min(running_speed)
    
    #np.savetxt(file_path.replace('.csv','_speed_per_bin.csv'), running_speed, fmt='%i', delimiter=',', newline='\n')
    #delete the desired number of rows/columns in the desired axis
    event_data = numpy.delete(behavior_and_event_data, (0,1,2,3,4,5,6,7,8,9,10,11), axis=0) #here we delete the first 12 rows, which contain the behavior data
    
    total_number_of_cells = event_data.shape[0]
    print 'Number of cells = %d' %total_number_of_cells
    
    total_number_of_frames = event_data.shape[1]
    print 'Number of imaging frames: %d'%total_number_of_frames
    

    
    ###############################################################################
    ## extract some parameters: enviorment transitions, odor sequence, track length
    ###############################################################################
    
    
    #find out the sequence in which odor environments were presented
    environment_sequence = [environment[1]] # save the first environment
    
    #remaining environments
    for column in range(1,total_number_of_frames):
        if(lap_count[column] > lap_count[column-1]):
            environment_sequence.append(environment[column])
    
    print 'Environments are presented in this sequence:'
    print environment_sequence

    laps_in_environment = numpy.zeros(number_of_environments,dtype='int')        
    for env in range(0,len(environment_sequence)):
        for current_env in range(0,number_of_environments):
            if(environment_sequence[env] == current_env+1):
                laps_in_environment[current_env] = laps_in_environment[current_env] + 1          



    ###############################################################################
    #################separate the different laps in each environment###############
    ###############################################################################


    if(split_laps_in_environment == 5050):
        environment = split_laps_into_earlier_and_later(environment,total_number_of_frames, lap_count,laps_in_environment)

        #after separating the odd and even trials of each environment, we have doubled the total number of environment in this context
        #number_of_environments = number_of_environments * 2
        number_of_environments = max(environment)
        print 'Number of environments after separating earlier and later trials = %d' %number_of_environments
    
        #find out the sequence in which odor environments were presented
        environment_sequence = [environment[1]] # save the first environment
        
        #remaining environments
        for column in range(1,total_number_of_frames):
            if(lap_count[column] > lap_count[column-1]):
                environment_sequence.append(environment[column])
        
        print 'Environments are presented in this sequence (after separating earlier and later trials):'
        print environment_sequence
    
        laps_in_environment = numpy.zeros(number_of_environments,dtype='int')        
        for env in range(0,len(environment_sequence)):
            for current_env in range(0,number_of_environments):
                if(environment_sequence[env] == current_env+1):
                    laps_in_environment[current_env] = laps_in_environment[current_env] + 1   
    
        print 'Number of laps in each enviornment after separating earlier and later trials:'
        print laps_in_environment

    elif(split_laps_in_environment == 1212):
        environment = split_laps_into_odd_and_even(environment,total_number_of_frames, lap_count)        
        
        #after separating the odd and even trials of each environment, we have doubled the total number of environment in this context
        #number_of_environments = number_of_environments * 2
        number_of_environments = max(environment)
        print 'Number of environments after separating even and odd trials = %d' %number_of_environments
    
        #find out the sequence in which odor environments were presented
        environment_sequence = [environment[1]] # save the first environment
        
        #remaining environments
        for column in range(1,total_number_of_frames):
            if(lap_count[column] > lap_count[column-1]):
                environment_sequence.append(environment[column])
        
        print 'Environments are presented in this sequence (after separating odd and even trials):'
        print environment_sequence
    
        laps_in_environment = numpy.zeros(number_of_environments,dtype='int')        
        for env in range(0,len(environment_sequence)):
            for current_env in range(0,number_of_environments):
                if(environment_sequence[env] == current_env+1):
                    laps_in_environment[current_env] = laps_in_environment[current_env] + 1   
    
        print 'Number of laps in each enviornment after separating odd and even trials:'
        print laps_in_environment

   
    ###############################################################################
    ###### end of steps to separate the different laps in each environment ########
    ###############################################################################    
    
          
        
    #find out the odor sequence for each environment
    #this is to print the correct odor sequence on the x-axis
    #and find out the track length in each environment 
      
    odor_sequence = numpy.zeros((number_of_environments*3),dtype='int')
    odor_start_and_end_points = numpy.zeros((number_of_environments*6),dtype='int')   # 3 odors, 3 start points + 3 end points = 6 total points
    env_track_lengths = numpy.zeros(number_of_environments,dtype='int')
    bins_in_environment = numpy.zeros(number_of_environments,dtype='int')
    env_starts_at_this_bin = numpy.zeros(number_of_environments+1,dtype='int')
    total_number_distance_bins_in_all_env = 0
    #expansion_factor = 0    
    ###############################################################################
    for env in range(0,number_of_environments):

        max_distance_point_in_env = 0
        for frame in range(1,total_number_of_frames):
            if(environment[frame] == env+1 and distance[frame] > max_distance_point_in_env):
                max_distance_point_in_env = distance[frame]
        env_track_lengths[env] = (max_distance_point_in_env / 2000) * 2000 #this will round down the distance value to the nearest multiple of 2000mm (hopefully giving us 2m, 4m or 8m values)

        #expansion_factor = env_track_lengths[env] / 4000  #just in case the virtual track has been expanded
        bins_in_environment[env] = env_track_lengths[env] / distance_bin_size
        env_starts_at_this_bin[env+1] = env_starts_at_this_bin[env] + bins_in_environment[env]
     

        #this part is for calculating the sequence of odors in each environment
        #at each encounter of new environment, we take note of every time a non-zero odor turns on/off and the distances at which this happens
        odor_count_in_this_sequence = 0
        lap_under_evaluation = 0
        for env_frame in range(1,total_number_of_frames):
            if(environment[env_frame] == env+1 and odor[env_frame] > odor[env_frame-1]):
                lap_under_evaluation = lap_count[env_frame]
                odor_sequence[env*3 + odor_count_in_this_sequence] = odor[env_frame]
                sum_of_odor_start_points = distance[env_frame] + odor_start_and_end_points[env*6 + odor_count_in_this_sequence*2]
                odor_start_and_end_points[env*6 + odor_count_in_this_sequence*2] = sum_of_odor_start_points #this is where the odor starts, distance has been rounded to nearest 50mm
            elif(environment[env_frame] == env+1 and odor[env_frame] < odor[env_frame-1]):
                sum_of_odor_end_points = distance[env_frame] + odor_start_and_end_points[env*6 + odor_count_in_this_sequence*2 + 1]
                odor_start_and_end_points[env*6 + odor_count_in_this_sequence*2 + 1] = sum_of_odor_end_points
                odor_count_in_this_sequence = odor_count_in_this_sequence + 1
            elif(lap_count[env_frame] > lap_under_evaluation or odor_count_in_this_sequence >= 3):
                odor_count_in_this_sequence = 0


        for odor_point in range(0,6):
            average_distance_odor_point = odor_start_and_end_points[env*6 + odor_point] / laps_in_environment[env]
            odor_start_and_end_points[env*6 + odor_point] = average_distance_odor_point

    ###############################################################################

    
    total_number_distance_bins_in_all_env = numpy.sum(bins_in_environment)
    
    print 'Odor sequence in each environment (3 odors per environment):'
    print odor_sequence

    print 'The odors turn on and off at these distance points along the track:'
    print odor_start_and_end_points

    odor_sequence_in_letters = [i for i in range(len(odor_sequence))] 
    #change odor labels from numbers to letters
    for odor in range (0,len(odor_sequence)):
        if (odor_sequence[odor] == 1):
            odor_sequence_in_letters[odor] = 'A'
        elif (odor_sequence[odor] == 2):
            odor_sequence_in_letters[odor] = 'B'        
        elif (odor_sequence[odor] == 3):
            odor_sequence_in_letters[odor] = 'C'     
        elif (odor_sequence[odor] == 4):
            odor_sequence_in_letters[odor] = 'D' 
        elif (odor_sequence[odor] == 5):
            odor_sequence_in_letters[odor] = 'E'             
        elif (odor_sequence[odor] == 6):
            odor_sequence_in_letters[odor] = 'F' 
        elif (odor_sequence[odor] == 7):
            odor_sequence_in_letters[odor] = 'G'
        else:
            odor_sequence_in_letters[odor] = ' '            
 
            
    print 'The odors were presented in this sequence (3 odors per environment):'
    print odor_sequence_in_letters
    print 'The track lengths in all enviornments are:'
    print env_track_lengths
    print 'Number of laps in each enviornment:'
    print laps_in_environment
    print 'Number of bins in each enviornment:'    
    print bins_in_environment
    print 'The odors start and end at these distance points:'
    print odor_start_and_end_points
    print 'New environment starts at bin:'
    print env_starts_at_this_bin
    print 'Total number of distance bins in all enviornments: %d'%total_number_distance_bins_in_all_env

    
    ###############################################################################    
    ###############################################################################
    ####################### calculate total events per bin ########################
    ###############################################################################
    
    total_events_per_bin_per_cell = numpy.zeros((total_number_of_cells,total_number_distance_bins_in_all_env),dtype='float')
    total_time_per_bin = numpy.zeros(total_number_distance_bins_in_all_env,dtype='float')    
    average_speed_per_bin = numpy.zeros(total_number_distance_bins_in_all_env,dtype='float')   
    
#    for cell in range(0,total_number_of_cells):    
#        if (cell % 50 == 0):
#            print 'Processing cell# %d / %d'%(cell,total_number_of_cells)    

    #run this while loop until all columns have been checked for the cell in this row
    last_bin_evaluated_for_total_time_per_bin = -1
    last_bin_evaluated_for_average_speed = -1
    last_lap_evaluated_for_events = -1
    have_not_reached_reward_region_in_this_lap = 1
    for frame in range(0,total_number_of_frames):
        if (frame % 1000 == 0):
            print 'Processing frame# %d / %d'%(frame,total_number_of_frames)
            
        track_length_in_this_lap = env_track_lengths[environment[frame]-1]
        #events get counted and summed in each bin only if the mouse is running above a threshold speed at the moment (e.g. 10cm/s in this case)
        if((distance[frame] < track_length_in_this_lap) and have_not_reached_reward_region_in_this_lap == 1):
            for cell in range(0,total_number_of_cells):          
                if (event_data[cell][frame] > 0 and running_speed[frame] > speed_threshold):
#                    current_bin = env_starts_at_this_bin[ lap_count[frame] / 50] + distance[frame] / distance_bin_size
                    current_bin = env_starts_at_this_bin[environment[frame]-1] + distance[frame] / distance_bin_size
                    current_bin_total_events = total_events_per_bin_per_cell[cell][current_bin] + event_data[cell][frame]
                    total_events_per_bin_per_cell[cell][current_bin] = current_bin_total_events

                #we only need to calculate the total time spent in a bin for one cell (this time has to be same for all cells, here we choose the zeroth cell)
                # 5.0cm is divided by speed to get the time spent in the current bin (speed was calculated as time required to cross each 50mm stretch of the track)
                if (cell == 0 and running_speed[frame] > speed_threshold):
#                    current_bin = env_starts_at_this_bin[ lap_count[frame] / 50] + distance[frame] / distance_bin_size
                    current_bin = env_starts_at_this_bin[environment[frame]-1] + distance[frame]/distance_bin_size
                    if(last_bin_evaluated_for_total_time_per_bin != current_bin):
                        last_bin_evaluated_for_total_time_per_bin = current_bin                   
                        total_time_spent_in_this_bin = total_time_per_bin[current_bin] + 50.0 / running_speed[frame] 
                        total_time_per_bin[current_bin] = total_time_spent_in_this_bin
                
                #calculate average speed per bin for each environment
                if (cell == 0):
#                    current_bin = env_starts_at_this_bin[ lap_count[frame] / 50] + distance[frame] / distance_bin_size
                    current_bin = env_starts_at_this_bin[environment[frame]-1] + distance[frame]/distance_bin_size
                    if(last_bin_evaluated_for_average_speed != current_bin):
                        last_bin_evaluated_for_average_speed = current_bin                   
                        sum_of_speeds = average_speed_per_bin[current_bin] + running_speed[frame]
                        average_speed_per_bin[current_bin] = sum_of_speeds


        elif((distance[frame] >= track_length_in_this_lap) and last_lap_evaluated_for_events < lap_count[frame]):
            have_not_reached_reward_region_in_this_lap = 0
            last_lap_evaluated_for_events = lap_count[frame]
        elif(last_lap_evaluated_for_events < lap_count[frame]):
            have_not_reached_reward_region_in_this_lap = 1
                            

    #np.savetxt(file_path.replace('.csv','_total_events_per_bin.csv'), total_events_per_bin_per_cell, fmt='%i', delimiter=',', newline='\n')                     
    #print total_time_per_bin
    print 'Total running time: %1.1f seconds'%numpy.sum(total_time_per_bin)

    #print average_speed_per_bin
    #print 'Normalized average speeds:'
    for current_bin in range(0,total_number_distance_bins_in_all_env):
        environment_in_this_bin = 0
        for env in range(0,number_of_environments-1):
            if(current_bin >= env_starts_at_this_bin[env] and current_bin < env_starts_at_this_bin[env+1]):
                environment_in_this_bin = env  
        average_speed_in_current_bin = average_speed_per_bin[current_bin] / laps_in_environment[environment_in_this_bin]
        average_speed_per_bin[current_bin] = average_speed_in_current_bin    
    #print average_speed_per_bin

    ###############################################################################
    ########################calculate events per lap ##############################
    ###############################################################################

    events_per_second_per_bin = numpy.zeros((total_number_of_cells,total_number_distance_bins_in_all_env),dtype='float') 
    for cell in range(0,total_number_of_cells): 
        for env_bin in range(0,total_number_distance_bins_in_all_env):
            if(total_time_per_bin[env_bin] > 1.00):
                #if(total_events_per_bin_per_cell[cell][env_bin] / total_time_per_bin[env_bin] > lower_threshold_for_activity):
                events_per_second_per_bin[cell][env_bin] = total_events_per_bin_per_cell[cell][env_bin] / total_time_per_bin[env_bin]
            else:
                events_per_second_per_bin[cell][env_bin] = 0.00
    #np.savetxt(file_path.replace('.csv','_events_per_second.csv'), events_per_second_per_bin, fmt='%1.2f', delimiter=',', newline='\n')


#    events_per_lap = np.zeros((total_number_of_cells,total_number_distance_bins_in_all_env),dtype='float')
#    #for env in range(0,number_of_environments):    
#    for env_bin in range(0,total_number_distance_bins_in_all_env):
#        
#        number_of_laps_in_this_bin = 0
#        for env_transition_bin in range(0,len(env_starts_at_this_bin)):
#            if(env_bin >= env_starts_at_this_bin[env_transition_bin] and env_bin < env_starts_at_this_bin[env_transition_bin+1]):
#                number_of_laps_in_this_bin = laps_in_environment[env_transition_bin]
#        if (number_of_laps_in_this_bin == 0):
#            print 'Something is weird here'
#        
#        for cell in range(0,total_number_of_cells): 
#            if(total_events_per_bin_per_cell[cell][env_bin] > 0):
#                events_per_lap[cell][env_bin] = total_events_per_bin_per_cell[cell][env_bin] / number_of_laps_in_this_bin
#    #np.savetxt(file_path.replace('.csv','_events_per_lap.csv'), events_per_lap, fmt='%1.2f', delimiter=',', newline='\n')





    ###############################################################################
    ########################calculate events per lap ##############################
    ###############################################################################

    gaussian_filtered_events_per_second = numpy.zeros((total_number_of_cells,total_number_distance_bins_in_all_env),dtype='float')

    #apply a one dimensional gaussian filter to event data for each cell:

    for env in range (0,number_of_environments):
        gaussian_filtered_event_data_in_this_env = ndimage.gaussian_filter1d(events_per_second_per_bin[:,env_starts_at_this_bin[env]:env_starts_at_this_bin[env+1]],sigma=gaussian_filter_sigma,axis=1)
        #gaussian_filtered_event_data_in_this_env = ndimage.gaussian_filter1d(events_per_lap[:,env_starts_at_this_bin[env]:env_starts_at_this_bin[env+1]],sigma=gaussian_filter_sigma,axis=1)
        
        for cell in range(0,gaussian_filtered_event_data_in_this_env.shape[0]): 
            for env_bin in range(0,gaussian_filtered_event_data_in_this_env.shape[1]):
                gaussian_filtered_events_per_second[cell][env_bin + env_starts_at_this_bin[env]] = gaussian_filtered_event_data_in_this_env[cell][env_bin]
        
        
    #np.savetxt(file_path.replace('.csv','_gaussian_filter_events_per_second.csv'), gaussian_filtered_events_per_second, fmt='%f', delimiter=',', newline='\n') 




    ###############################################################################
    ############generate ranking for cells according to max response###############
    ###############################################################################

    place_data_each_cell = numpy.zeros((total_number_of_cells,total_number_distance_bins_in_all_env+2*number_of_environments),dtype='float')
        
    for cell in range(0,total_number_of_cells): 
        cell_max_response = numpy.max(gaussian_filtered_events_per_second[cell,:])
        for env in range(0,number_of_environments):
            env_max_response_column = 0
            env_max_response = 0.00
            for env_bin in range(env_starts_at_this_bin[env],env_starts_at_this_bin[env+1]):
                if (gaussian_filtered_events_per_second[cell][env_bin] > env_max_response):
                    env_max_response_column = env_bin
                    env_max_response = gaussian_filtered_events_per_second[cell][env_bin] 
            if(env_max_response_column == 0 and env_max_response == 0.00):
                place_data_each_cell[cell][2*env]= -1
                place_data_each_cell[cell][2*env+1]= env_max_response
            elif(cell_max_response >= lower_threshold_for_activity):
                place_data_each_cell[cell][2*env]= env_max_response_column
                place_data_each_cell[cell][2*env+1]= env_max_response                
                
                for column in range(2*number_of_environments + env_starts_at_this_bin[env],2*number_of_environments + env_starts_at_this_bin[env]+bins_in_environment[env]):
                    #if(env_max_response > lower_threshold_for_activity):
                    place_data_each_cell[cell][column] = gaussian_filtered_events_per_second[cell][column-2*number_of_environments] / cell_max_response
#    print total_time_per_bin
#    np.savetxt(file_path.replace('.csv','_total_events_per_bin.csv'), total_events_per_bin_per_cell, fmt='%i', delimiter=',', newline='\n') 
#    np.savetxt(file_path.replace('.csv','_events_per_lap.csv'), events_per_lap, fmt='%1.2f', delimiter=',', newline='\n')
#    np.savetxt(file_path.replace('.csv','_gaussian_filter_events_per_second.csv'), gaussian_filtered_event_data, fmt='%f', delimiter=',', newline='\n') 
#    np.savetxt(file_path.replace('.csv','_gaussian_filtered_events_per_second_ranked.csv'), place_data_each_cell, fmt='%f', delimiter=',', newline='\n')            

    #now send the data for plotting:
#    generate_plots(file_path, place_data_each_cell,total_time_per_bin,number_of_environments, laps_in_environment, total_number_of_cells, bins_in_environment, env_starts_at_this_bin,env_track_lengths,odor_sequence_in_letters,distance_bin_size,odor_start_and_end_points,speed_threshold,total_number_distance_bins_in_all_env,gaussian_filter_sigma,lower_threshold_for_activity,average_speed_per_bin,split_laps_in_environment)

    ###############################################################################
    ########################done generating data for plots ########################
    ###############################################################################


###############################################################################
###############################################################################
###################### now we plot some good nice heatmaps ####################
###############################################################################
###############################################################################
#based on source: http://stackoverflow.com/questions/14391959/heatmap-in-matplotlib-with-pcolor
#def generate_plots(file_path, place_field_events_each_cell,total_time_per_bin,number_of_environments, laps_in_environment, total_number_of_cells, bins_in_environment, env_starts_at_this_bin,env_track_lengths,odor_sequence,distance_bin_size,odor_start_and_end_points,speed_threshold,total_number_distance_bins_in_all_env,gaussian_filter_sigma,lower_threshold_for_activity,average_speed_per_bin,split_laps_in_environment):

    #to stamp each figure heading with the mouse ID and date of recording

    # for file names of the format wfnjC19_2015-02-14_behavior_and_events.csv , this straightforward method of extracting the mouse ID and date will work
    #name_of_this_file = file_path[-42:-24] #

    #however, if the filename is in a different format, we will look for the first instance of the letter 'w' from the end of the filename
    filename_starts_at_this_letter = 0
    file_length = len(file_path)
    for name_letter in range (1,file_length):
        if(file_path[file_length - name_letter] == 'w' or file_path[file_length - name_letter] == 'W'):
            filename_starts_at_this_letter = file_length - name_letter
            break
    name_of_this_file = file_path[filename_starts_at_this_letter:(filename_starts_at_this_letter+18)]

    print 'Mouse ID name is: %s'%name_of_this_file

    sequence_of_environments = ''
    for env in range(0,number_of_environments):
        sequence_of_environments = sequence_of_environments + odor_sequence_in_letters[3*env] + odor_sequence_in_letters[3*env+1] + odor_sequence_in_letters[3*env+2]
        if(env < number_of_environments-1):
            sequence_of_environments = sequence_of_environments + '-'
    print 'This is the sequence of environments: %s' %sequence_of_environments


    figs = []
#    env_aligned_to_itself_figs = []


    #heatmap_colors = ['Blues','Greens','BuPu','Oranges','Purples','Reds','RdPu','PuBu']
    #use a different plot legend color for each environment
    #plot_color = ['r','b','g','m','c','y']  
    plot_color = ['r','r','r','r','r','r'] 
    earlierORlater=['(earlier trials)','(later trials)','(earlier trials)','(later trials)']            
    oddOReven=['(odd trials)','(even trials)','(odd trials)','(even trials)']

    
    for plot_env in range (0,number_of_environments):
        data_array_all = place_data_each_cell[numpy.argsort(place_data_each_cell[:,plot_env*2],kind='quicksort')]
        
        data_array = []
        for row in range(0,data_array_all.shape[0]):
            if(data_array_all[row][2*plot_env] >= 0 and data_array_all[row][2*plot_env+1]>=lower_threshold_for_activity):
                if(len(data_array) == 0):
                    data_array = data_array_all[row,:]
                else:
                    data_array = numpy.vstack([data_array, data_array_all[row,:]])
        
        if(len(data_array) == 0):
            data_array = numpy.zeros((2,data_array_all.shape[1]))
        elif(len(data_array) == data_array_all.shape[1]):
            data_array = numpy.vstack([numpy.zeros((1,data_array_all.shape[1])),data_array])            
        
        #np.savetxt(file_path.replace('.csv','_plotted_data_sorted_for_env_%d.csv'%plot_env), data_array[:,0:2*number_of_environments], fmt='%f', delimiter=',', newline='\n')   

        #for env in range (plot_env,plot_env+1):
        for env in range (0,number_of_environments):
            fig = plt.figure()
            fig.subplots_adjust(hspace=0)
            fig.set_rasterized(True)

            if(split_laps_in_environment == 5050):            
                fig.suptitle('%s    env %d %s plotted against env %d %s' %(name_of_this_file, env+1,earlierORlater[env],plot_env+1,earlierORlater[plot_env]))
            elif(split_laps_in_environment == 1212):            
                fig.suptitle('%s    env %d %s plotted against env %d %s' %(name_of_this_file, env+1,oddOReven[env],plot_env+1,oddOReven[plot_env]))
            else:
                fig.suptitle('%s    env %d place cell activity plotted against env %d' %(name_of_this_file, env+1,plot_env+1))  


            ax  = plt.subplot2grid((1,1), (0,0), rowspan=4,colspan=4)
            
            #to label the odor sequence on the plots
            od = odor_sequence_in_letters[env*3:(env+1)*3] 
            sort_od = odor_sequence_in_letters[plot_env*3:(plot_env+1)*3]

            odor_label1 = 0.13 + 0.60 * (float(odor_start_and_end_points[env*6+0]) / float(env_track_lengths[env]))
            odor_label2 = 0.13 + 0.60 * (float(odor_start_and_end_points[env*6+2]) / float(env_track_lengths[env]))            
            odor_label3 = 0.13 + 0.60 * (float(odor_start_and_end_points[env*6+4]) / float(env_track_lengths[env]))            
            
           
            plt.figtext(odor_label1,0.91, "%s"%od[0], fontsize='large', color=plot_color[plot_env], ha ='left')
            plt.figtext(odor_label2,0.91, "%s"%od[1], fontsize='large', color=plot_color[plot_env], ha ='left')
            plt.figtext(odor_label3,0.91, "%s"%od[2], fontsize='large', color=plot_color[plot_env], ha ='left')            

            plt.figtext(0.84,0.88,"Env sequence:",                                         fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.85,"%s" %sequence_of_environments,                          fontsize='x-small', color=plot_color[plot_env], ha ='left')

            plt.figtext(0.84,0.75, "Current environment:",                                 fontsize='xx-small', color=plot_color[plot_env], ha ='left') 
            plt.figtext(0.84,0.7, "%d - %s%s%s"%(env+1,od[0],od[1],od[2]),                 fontsize='large', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.65, "Sort reference env:",                                  fontsize='xx-small', color=plot_color[plot_env], ha ='left') 
            plt.figtext(0.84,0.6, "%d - %s%s%s"%(plot_env+1,sort_od[0],sort_od[1],sort_od[2]), fontsize='large', color=plot_color[plot_env], ha ='left')

            plt.figtext(0.84,0.5,"Environments: %d" %number_of_environments,               fontsize='x-small', color=plot_color[plot_env], ha ='left')           
            plt.figtext(0.84,0.45,"Bin size: %dmm" %distance_bin_size,                     fontsize='x-small', color=plot_color[plot_env], ha ='left')            
            plt.figtext(0.84,0.4,"Track: %1.1fm" %(env_track_lengths[env]/1000.0),         fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.35,"Laps: %d" %laps_in_environment[env],                    fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.3,"Total cells: %d" %total_number_of_cells,                 fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.25,"min speed: %dmm/s" %speed_threshold,                    fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.2,"Sigma: %1.1f" %gaussian_filter_sigma,                    fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.15,"min.activity: %1.3f" %lower_threshold_for_activity,     fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.1,"Cells in env: %d" %data_array.shape[0],                  fontsize='x-small', color=plot_color[plot_env], ha ='left')
            
            plt.figtext(0.03,0.15,"%d" %data_array.shape[0],                               fontsize='large', color = plot_color[plot_env], ha ='left')
            plt.figtext(0.02,0.10,"cells",                                                 fontsize='large', color = plot_color[plot_env], ha ='left')

    
            #if(plot_env%2 == 0):
            #heatmap = ax.pcolor(normalized_data_array, cmap=plt.cm.Blues) 
            heatmap = ax.pcolormesh(data_array[:,env_starts_at_this_bin[env]+2*number_of_environments:env_starts_at_this_bin[env+1]+2*number_of_environments], cmap=plt.cm.jet,vmin=0.00,vmax=1.00) 
            color_legend = plt.colorbar(heatmap,aspect=30)
            color_legend.ax.tick_params(labelsize=5) 
            #color_legend.set_label('evets per second')
            plt.figtext(0.765,0.6,'events per sec (normalized to max bin)',fontsize='x-small',rotation=90)
            
#            #ax.set_title('%1.1fm track x %d laps     Odor sequence:%s%s%s%s'%(environment_track_lengths[env]/1000.00,laps_in_environment[env],od[0],od[1],od[2],od[3]), fontsize='x-small')
#            ax.set_xlabel('Distance bin (%d mm each)'%distance_bin_size)
#            ax.xaxis.tick_bottom() 
#            plt.setp(ax.get_xticklabels(),visible=True)

            ax.xaxis.tick_bottom()
            x1 = float(env_track_lengths[env])
            x2 = x1 / (8 * 1000) # there are eight points on the x-axis, other than the 0
            x3 = [x2*0, x2*1 , x2*2 , x2*3 , x2*4 , x2*5 , x2*6 , x2*7 , x2*8 ]
            ax.set_xlabel('Distance(m)')
            plt.setp(ax,xticklabels=x3,visible=True)
           
            plt.xlim (0,bins_in_environment[env])
            plt.ylim (0,data_array.shape[0]) 
            plt.gca().invert_yaxis()

                        
            #draw white lines to mark odor regions
            plt.axvline(x=odor_start_and_end_points[env*6+0]/distance_bin_size, linewidth=0.2, color='w')
            plt.axvline(x=odor_start_and_end_points[env*6+1]/distance_bin_size, linewidth=0.2, color='w')
            plt.axvline(x=odor_start_and_end_points[env*6+2]/distance_bin_size, linewidth=0.2, color='w')
            plt.axvline(x=odor_start_and_end_points[env*6+3]/distance_bin_size, linewidth=0.2, color='w')
            plt.axvline(x=odor_start_and_end_points[env*6+4]/distance_bin_size, linewidth=0.2, color='w')
            plt.axvline(x=odor_start_and_end_points[env*6+5]/distance_bin_size, linewidth=0.2, color='w')

            #plt.axvline(x=odor_start_points[env*5+4]/distance_bin_size, linewidth=0.5, color='r')
            #plt.axvspan(odor_start_points[env*5+4]/distance_bin_size, (odor_start_points[env*5+4]+odor_start_points[env*5+0]*3)/distance_bin_size, facecolor='r', alpha=0.1)
                
            #plt.setp(ax.get_yticklabels(), visible=True)

            ax.yaxis.set_major_locator(MaxNLocator(integer=True)) 
            ax.set_ylabel('Cell#')
            fig.add_subplot(ax)
     
            #can be commented out to stop showing all plots in the console
            plt.show()
            figs.append(fig)
#            if (env == plot_env):
#                env_aligned_to_itself_figs.append(fig)                
            plt.close()


###############################################################################
####### generate plots for normalized average speed in each environment #######
###############################################################################

    for env in range (0,number_of_environments):
        fig = plt.figure()
        fig.subplots_adjust(hspace=0)
        fig.set_rasterized(True)
        
        
        if(split_laps_in_environment == 5050):            
            fig.suptitle('%s    env %d %s average speed (normalized to max)' %(name_of_this_file, env+1,earlierORlater[env]))
        elif(split_laps_in_environment == 1212):            
            fig.suptitle('%s    env %d %s average speed (normalized to max)' %(name_of_this_file, env+1,oddOReven[env]))
        else:
            fig.suptitle('%s    env %d average speed (normalized to max)' %(name_of_this_file, env+1))


        this_env_average_speed_per_bin = average_speed_per_bin[env_starts_at_this_bin[env]:env_starts_at_this_bin[env+1]] 
        
        max_average_speed = max(this_env_average_speed_per_bin)
        normalized_average_speed = [(x / max_average_speed) for x in this_env_average_speed_per_bin]

        
        ax1 = plt.subplot2grid((1,1), (0,0), rowspan=1,colspan=1)
        plt.plot(range(bins_in_environment[env]),normalized_average_speed,'r-', linewidth = 0.1)
        #ax1.set_xlabel('Distance bin (%d mm each)'%distance_bin_size)
        ax1.set_ylabel('Normalized Average Speed',fontsize='large')
        ax1.set_ylim(0,1)
        plt.tick_params(axis='y', which='both', labelleft='on', labelright='on')
        plt.setp(ax1.get_yticklabels(),visible=True)

        ax1.xaxis.tick_bottom()
        x1 = float(env_track_lengths[env])
        x2 = x1 / (8 * 1000) # there are eight points on the x-axis, other than the 0
        x3 = [x2*0, x2*1 , x2*2 , x2*3 , x2*4 , x2*5 , x2*6 , x2*7 , x2*8 ]
        ax1.set_xlabel('Distance(m)')
        plt.setp(ax1,xticklabels=x3,visible=True)

        #to label the odor sequence on the plots
        od = odor_sequence_in_letters[env*3:(env+1)*3]

        odor_label1 = 0.13 + 0.75 * (float(odor_start_and_end_points[env*6+0]) / float(env_track_lengths[env]))
        odor_label2 = 0.13 + 0.75 * (float(odor_start_and_end_points[env*6+2]) / float(env_track_lengths[env]))            
        odor_label3 = 0.13 + 0.75 * (float(odor_start_and_end_points[env*6+4]) / float(env_track_lengths[env])) 
        
        plt.figtext(odor_label1,0.91, "%s"%od[0], fontsize='large', color=plot_color[plot_env], ha ='left')
        plt.figtext(odor_label2,0.91, "%s"%od[1], fontsize='large', color=plot_color[plot_env], ha ='left')
        plt.figtext(odor_label3,0.91, "%s"%od[2], fontsize='large', color=plot_color[plot_env], ha ='left') 
        
        #color_legend = plt.colorbar(heatmap,aspect=30)
        #fig.delaxes(fig.axes[3]) #here axis 0 = plot in ax, 1 = colorbar in ax, 2 = plot in ax1, 3 = heatmap in ax1

        plt.axvline(x=odor_start_and_end_points[env*6+0]/distance_bin_size, linewidth=0.2, color='b')
        plt.axvline(x=odor_start_and_end_points[env*6+1]/distance_bin_size, linewidth=0.2, color='b')
        plt.axvline(x=odor_start_and_end_points[env*6+2]/distance_bin_size, linewidth=0.2, color='r')
        plt.axvline(x=odor_start_and_end_points[env*6+3]/distance_bin_size, linewidth=0.2, color='r')
        plt.axvline(x=odor_start_and_end_points[env*6+4]/distance_bin_size, linewidth=0.2, color='m')
        plt.axvline(x=odor_start_and_end_points[env*6+5]/distance_bin_size, linewidth=0.2, color='m')
 
        fig.add_subplot(ax1)
        plt.show()
        figs.append(fig)               
        plt.close()

###############################################################################
#### done generating plots for normalized average speed in each environment ###
###############################################################################
    
    if len(figs) > 0: 
        pp = PdfPages(plot_pdf_name)
        for fig in figs:
                pp.savefig(fig,dpi=300,edgecolor='r')
        pp.close()

###############################################################################

main()