import matplotlib.pyplot as plt # needed for plotting graphs
import numpy as np # needed for various math tasks
from matplotlib.ticker import MaxNLocator #y-axis labels
from matplotlib.backends.backend_pdf import PdfPages # for saving figures as pdf
import os # needed to arrange filenames alphabetically
import re # needed to arrange filenames alphabetically
from scipy import ndimage # needed to apply gaussian filter


def main():
    #for PC, the format is something like: directory_path ='C:/Users/axel/Desktop/test_data'
    directory_path ='/Users/njoshi/Desktop/events_test'
    distance_bin_size = 50 #distance bin in mm
    speed_threshold = 50 #minimum speed in mm/s for selecting events
    gaussian_filter_sigma = 2.00
    lower_threshold_for_activity = 0.20
    time_bin_size = 200 #time bin in ms
    number_of_time_bins = 0 #number of time bins for each environment, use value=0 if you want the script to automatically determine the number of bins

    
    file_names = [os.path.join(directory_path, f)
        for dirpath, dirnames, files in os.walk(directory_path)
        for f in files if f.endswith('.csv')]
    file_names.sort(key=natural_key)
    
    for mouse_data in file_names:
        print 'Analyzing this file: '+ mouse_data
#        if os.path.isfile(mouse_data.replace(".csv","_sorted_place_cells.pdf")):
#            print 'A pdf already exists for this file. Delete the pdf to generate a new one.'
#        else:
        read_data_and_generate_plots(mouse_data, distance_bin_size,speed_threshold,gaussian_filter_sigma,lower_threshold_for_activity,time_bin_size,number_of_time_bins)


#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def read_data_and_generate_plots(file_path, distance_bin_size,speed_threshold,gaussian_filter_sigma,lower_threshold_for_activity,time_bin_size,number_of_time_bins):
    
    event_data = np.loadtxt(file_path, dtype='int', delimiter=',')
    #event_data = event_data[0:22,0:5]
    #to plot time as x-axis, transpose the whole array
    event_data = event_data.transpose()
    print 'In this recording:'
    print "Events array size is: (%d ,%d)" %(event_data.shape[0], event_data.shape[1])
    
    #row 0 = frame number
    #row 1 = time
    #row 2 = odor
    #row 3 = licks
    #row 4 = rewards
    #row 5 = distance
    #row 6 = lap
    #row 7 = environment
    #row 8 = speed
    #row 9 to last row = event data for cells in this recording
    
    time_stamp = event_data[1,:]

    odor = event_data[2,:]
    lap_count = event_data[6,:]
    total_laps = max(lap_count) + 1
    print 'Number of laps = %d' %total_laps
    
    average_time_for_lap_completion = max(time_stamp)/(total_laps * 1000)
    print 'Average time for lap completion = %d s' %average_time_for_lap_completion
    
    distance = event_data[5,:] 
    environment = event_data[7,:]
    
    number_of_environments = max(environment)
    print 'Number of environments = %d' %number_of_environments

    
    running_speed = event_data[8,:]
    print 'Maximum speed was: %f' %max(running_speed)    
    print 'Minimum speed was: %f' %min(running_speed)
    
    #np.savetxt(file_path.replace('.csv','_speed_per_bin.csv'), running_speed, fmt='%i', delimiter=',', newline='\n')
    #delete the desired number of rows/columns in the desired axis
    event_data = np.delete(event_data, (0,1,2,3,4,5,6,7,8), axis=0) #here we delete the first 8 rows, which contain the behavior data
    
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

    laps_in_environment = np.zeros(number_of_environments,dtype='int')        
    for env in range(0,len(environment_sequence)):
        for current_env in range(0,number_of_environments):
            if(environment_sequence[env] == current_env+1):
                laps_in_environment[current_env] = laps_in_environment[current_env] + 1          




    ###############################################################################
    #################separate the different laps in each environment###############
    ############ uncomment to choose odd vs even or earlier vs later ##############
    ###############################################################################
       
#    #################separate odd and even trials of each environment#################
#    last_env1 = 3
#    last_env2 = 4
#    for frame in range(0,total_number_of_frames-1):
#        frame_env = environment[frame]
#        frame_lap = lap_count[frame]
#        next_frame_lap = lap_count[frame+1]
#
#        if(frame_lap == next_frame_lap and frame_env == 1 and last_env1 == 3):
#            environment[frame] = 1
#        elif(next_frame_lap == frame_lap+1 and frame_env == 1 and last_env1 == 3):
#            environment[frame] = 1
#            last_env1 = 1
#
#        elif(frame_lap == next_frame_lap and frame_env == 1 and last_env1 == 1):
#            environment[frame] = 3
#        elif(next_frame_lap == frame_lap+1 and frame_env == 1 and last_env1 == 1):
#            environment[frame] = 3
#            last_env1 = 3
#
#        elif(frame_lap == next_frame_lap and frame_env == 2 and last_env2 == 4):
#            environment[frame] = 2
#        elif(next_frame_lap == frame_lap+1 and frame_env == 2 and last_env2 == 4):
#            environment[frame] = 2
#            last_env2 = 2
#
#        elif(frame_lap == next_frame_lap and frame_env == 2 and last_env2 == 2):
#            environment[frame] = 4
#        elif(next_frame_lap == frame_lap+1 and frame_env == 2 and last_env2 == 2):
#            environment[frame] = 4
#            last_env2 = 4
#        else:
#            environment[frame] = -1  
#
#    environment[len(environment) -1] = environment[len(environment) -2]
#    ################# done separating odd and even trials of each environment#################


#    #################separate the earlier and later trials of each environment equally#################
#    env1_half_laps = laps_in_environment[0] / 2
#    env2_half_laps = laps_in_environment[1] / 2
#    
#    env1_lap_count = 0
#    env2_lap_count = 0
#    
#    for frame in range(0,total_number_of_frames-1):
#        frame_env = environment[frame]
#        frame_lap = lap_count[frame]
#        next_frame_lap = lap_count[frame+1]
#
#        if(frame_lap == next_frame_lap and frame_env == 1 and env1_lap_count < env1_half_laps):
#            environment[frame] = 1
#        elif(next_frame_lap == frame_lap+1 and frame_env == 1 and env1_lap_count < env1_half_laps):
#            environment[frame] = 1
#            env1_lap_count = env1_lap_count + 1
#
#        elif(frame_lap == next_frame_lap and frame_env == 1 and env1_lap_count >= env1_half_laps):
#            environment[frame] = 3
#        elif(next_frame_lap == frame_lap+1 and frame_env == 1 and env1_lap_count >= env1_half_laps):
#            environment[frame] = 3
#            env1_lap_count = env1_lap_count + 1
#
#        elif(frame_lap == next_frame_lap and frame_env == 2 and env2_lap_count < env2_half_laps):
#            environment[frame] = 2
#        elif(next_frame_lap == frame_lap+1 and frame_env == 2 and env2_lap_count < env2_half_laps):
#            environment[frame] = 2
#            env2_lap_count = env2_lap_count + 1
#
#        elif(frame_lap == next_frame_lap and frame_env == 2 and env2_lap_count >= env2_half_laps):
#            environment[frame] = 4
#        elif(next_frame_lap == frame_lap+1 and frame_env == 2 and env2_lap_count >= env2_half_laps):
#            environment[frame] = 4
#            env2_lap_count = env2_lap_count + 1
#        else:
#            environment[frame] = -1  
#
#    environment[len(environment) -1] = environment[len(environment) -2]
#
#    print env1_half_laps
#    print env2_half_laps    
#    print 'Env 1 total lap count is: %d'%env1_lap_count
#    print 'Env 2 total lap count is: %d'%env2_lap_count
#    ############### done separating the earlier and later trials of each environment equally############
#
#
#
#
#    
#    #after separating the odd and even trials of each environment, we have doubled the total number of environment in this context
#    #number_of_environments = number_of_environments * 2
#    number_of_environments = max(environment)
#    print 'Number of environments after separating even and odd trials = %d' %number_of_environments
#
#    #find out the sequence in which odor environments were presented
#    environment_sequence = [environment[1]] # save the first environment
#    
#    #remaining environments
#    for column in range(1,total_number_of_frames):
#        if(lap_count[column] > lap_count[column-1]):
#            environment_sequence.append(environment[column])
#    
#    print 'Environments are presented in this sequence (after separating odd and even trials):'
#    print environment_sequence
#
#    laps_in_environment = np.zeros(number_of_environments,dtype='int')        
#    for env in range(0,len(environment_sequence)):
#        for current_env in range(0,number_of_environments):
#            if(environment_sequence[env] == current_env+1):
#                laps_in_environment[current_env] = laps_in_environment[current_env] + 1   
#
#    print 'Number of laps in each enviornment after separating odd and even trials:'
#    print laps_in_environment
#   
#    ###############################################################################
#    ###### end of steps to separate the different laps in each environment ########
#    ###############################################################################  





    ###############################################################################    
    
    #find out the odor sequence for each environment
    #this is to print the correct odor sequence on the x-axis
    #and find out the track length in each environment 

    # I read online that python runs much faster if you specify an empty list/array first and then fill it up
    # instead of building up the list by appending each new element to a shorter list
    # so here I am assuming that the minimum speed a mouse is at least 20 cm/s to get a large empty list that will hopefully fit all time bins in all cases

      
    odor_sequence = np.zeros((number_of_environments*3),dtype='int')
    odor_start_and_end_points = np.zeros((number_of_environments*6),dtype='int')   # 3 odors, 3 start points + 3 end points = 6 total points
    env_track_lengths = np.zeros(number_of_environments,dtype='int')
    bins_in_environment = np.zeros(number_of_environments,dtype='int')
    env_starts_at_this_bin = np.zeros(number_of_environments+1,dtype='int')
    total_number_distance_bins_in_all_env = 0
    expansion_factor = 0
    
    for env in range(0,number_of_environments):

        max_distance_point_in_env = 0
        for frame in range(1,total_number_of_frames):
            if(environment[frame] == env+1 and distance[frame] > max_distance_point_in_env):
                max_distance_point_in_env = distance[frame]
        env_track_lengths[env] = (max_distance_point_in_env / 2000) * 2000 #this will round down the distance value to the nearest multiple of 2000mm (hopefully giving us 2m, 4m or 8m values)

        expansion_factor = env_track_lengths[env] / 4000  #just in case the virtual track has been expanded
        if(number_of_time_bins > 0):           
            bins_in_environment[env] = number_of_time_bins #if you want to manually specify the number of bins for the environments
        else:
            bins_in_environment[env] = (env_track_lengths[env] * 5) / time_bin_size #this is for automatically specifying the number of bins per environment based on track length
            #bins_in_environment[env] = 80 + ((expansion_factor * average_time_for_lap_completion)/15)*80   #this will automatically specify the number of bins per environment based on average time for lap completion
        env_starts_at_this_bin[env+1] = env_starts_at_this_bin[env] + bins_in_environment[env]
     
        odor_start_and_end_points[env*6 + 0] = 1000*expansion_factor #this is where the odor starts
        odor_start_and_end_points[env*6 + 1] = 1500*expansion_factor
        odor_start_and_end_points[env*6 + 2] = 2000*expansion_factor
        odor_start_and_end_points[env*6 + 3] = 2500*expansion_factor
        odor_start_and_end_points[env*6 + 4] = 3000*expansion_factor
        odor_start_and_end_points[env*6 + 5] = 3500*expansion_factor


        for column in range(1,total_number_of_frames):
            if(environment[column] == env + 1): #look at first lap of the new environment
                if(distance[column] > odor_start_and_end_points[env*6 + 0] and distance[column] < odor_start_and_end_points[env*6 + 1] and odor_sequence[env*3+0] <= 0):  #find first odor
                    odor_sequence[env*3+0] = odor[column]
                elif(distance[column] > odor_start_and_end_points[env*6 + 2] and distance[column] < odor_start_and_end_points[env*6 + 3] and odor_sequence[env*3+1] <= 0):  #find second odor
                    odor_sequence[env*3+1] = odor[column]
                elif(distance[column] > odor_start_and_end_points[env*6 + 4] and distance[column] < odor_start_and_end_points[env*6 + 5] and odor_sequence[env*3+2] <= 0):  #find third odor
                    odor_sequence[env*3+2] = odor[column] 

    total_number_of_time_bins_in_all_env = np.sum(bins_in_environment)
    
    print 'The odor numbers (3 odors per environment):'
    print odor_sequence

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
            odor_sequence_in_letters[odor] = '0'            
 
            
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





    ############################################################################################################################################################## 
    ############################################################################################################################################################## 
    ############################################################################################################################################################## 
    ##############################################################################################################################################################     
    ##############################################################################################################################################################    
    ############################################################################################################################################################## 
    ####################### calculate total events per bin ####################################################################################################### 
    ############################################################################################################################################################## 
    ############################################################################################################################################################## 
    ############################################################################################################################################################## 
    ############################################################################################################################################################## 
    ############################################################################################################################################################## 
    
    total_time_events_per_bin = np.zeros((total_number_of_cells,total_number_of_time_bins_in_all_env),dtype='float')
    times_for_lap_completion = np.zeros(total_laps,dtype='float')
#    times_for_reaching_reward_location = np.zeros(total_laps,dtype='float')

#    for cell in range(0,total_number_of_cells):    
#        if (cell % 50 == 0):
#            print 'Processing cell# %d / %d'%(cell,total_number_of_cells)            

    lap_under_evaluation = 0
    last_lap_evaluated = -1
    lap_start_time = 0
#        event_count = 0

    # consider using a for loop based on laps instead of frames

    #run thi for loop until all columns have been checked for the cell in this row
    for frame in range(0,total_number_of_frames):

        if (frame % 1000 == 0):
            print 'Processing frame# %d / %d'%(frame,total_number_of_frames)   

        track_length_in_this_lap = env_track_lengths[environment[frame]-1]
        
        #this if statement makes sure that we add up only the events that occur before the start of reward period
        #also determine if the event is within the evaluated part of the lap
        if(lap_count[frame] == lap_under_evaluation and lap_under_evaluation > last_lap_evaluated and running_speed[frame] >= speed_threshold and distance[frame] < track_length_in_this_lap):                      
            lap_start_time = time_stamp[frame]
            last_lap_evaluated = lap_under_evaluation
#                if(cell == 0 and lap_count[frame] < 50):
#                    print 'lap %d starts at %d' %(lap_under_evaluation,lap_start_time)
#                current_time_bin = env_starts_at_this_bin[environment[frame]-1] + ((time_stamp[frame] - lap_start_time) / time_bin_size)
#                total_events_in_current_time_bin = total_time_events_per_bin[cell][current_time_bin] + event_data[cell][frame]  #add up the events in this bin
#                total_time_events_per_bin[cell][current_time_bin] = total_events_in_current_time_bin
#                if(cell == 1 and event_data[cell][frame] == 1):
#                    event_count = event_count+1
#                    print 'added special event %d in bin %d' %(event_count,current_time_bin)

        elif(lap_count[frame] == lap_under_evaluation and lap_under_evaluation == last_lap_evaluated and running_speed[frame] >= speed_threshold and distance[frame] < track_length_in_this_lap):
            current_time_bin = env_starts_at_this_bin[environment[frame]-1] + ((time_stamp[frame] - lap_start_time) / time_bin_size)
            if(current_time_bin >= env_starts_at_this_bin[environment[frame]]):
                print 'current lap is %d'%lap_under_evaluation
                print 'increase the number of time bins and reanalyze this file'
                break

            #if(current_time_bin < env_starts_at_this_bin[environment[frame]]):
            for cell in range(0,total_number_of_cells):
                if(event_data[cell][frame] > 0):
                    total_events_in_current_time_bin = total_time_events_per_bin[cell][current_time_bin] + event_data[cell][frame]  #add up the events in this bin
                    total_time_events_per_bin[cell][current_time_bin] = total_events_in_current_time_bin

#                if(cell < 5 and event_data[cell][frame] == 1):
#                    event_count = event_count+1
#                    print 'added event %d in bin %d current bin total is %d' %(event_count,current_time_bin,total_events_in_current_time_bin)

        elif(lap_count[frame] == lap_under_evaluation and last_lap_evaluated == lap_under_evaluation and distance[frame] >= track_length_in_this_lap):
#                if(cell == 0 and lap_count[frame] < 20):
#                    print distance[frame]
#                    print env_track_lengths[environment[frame]-1]
#                    print 'lap %d ends at %d ms when mouse reaches reward region' %(lap_under_evaluation,time_stamp[frame])
            times_for_lap_completion[lap_under_evaluation] = time_stamp[frame] - lap_start_time
            lap_under_evaluation = lap_count[frame] + 1
            
        elif(lap_count[frame] == lap_under_evaluation and last_lap_evaluated == lap_under_evaluation and running_speed[frame] < speed_threshold): 
            times_for_lap_completion[lap_under_evaluation] = time_stamp[frame] - lap_start_time
            lap_under_evaluation = lap_count[frame] + 1


#    np.savetxt(file_path.replace('.csv','_raw_events.csv'), event_data, fmt='%i', delimiter=',', newline='\n') 
#    np.savetxt(file_path.replace('.csv','_total_events_per_bin.csv'), total_time_events_per_bin, fmt='%i', delimiter=',', newline='\n') 
#    np.savetxt(file_path.replace('.csv','_time_in_each_lap.csv'), times_for_lap_completion, fmt='%i', delimiter=',', newline='\n')



    ############################################################################################################################################################## 
    ############################################################################################################################################################## 
    ############################################################################################################################################################## 
    ############################################################################################################################################################## 
    ############################################################################################################################################################## 
    ############################################################################################################################################################## 
    ############################################################################################################################################################## 


    ###############################################################################
    ########################calculate events per lap ##############################
    ###############################################################################

    events_per_second_per_bin = np.zeros((total_number_of_cells,total_number_of_time_bins_in_all_env),dtype='float') 
    for cell in range(0,total_number_of_cells): 
        for env_bin in range(0,total_number_of_time_bins_in_all_env):
            current_environment = 0
            for env in range(0,number_of_environments-1):
                if(env_bin >= env_starts_at_this_bin[env] and env_bin < env_starts_at_this_bin[env+1]):
                    current_environment = env
            if(total_time_events_per_bin[cell][env_bin] > 0):
                events_per_second_per_bin[cell][env_bin] = (total_time_events_per_bin[cell][env_bin] * 1000) / (time_bin_size * laps_in_environment[current_environment] )
#    np.savetxt(file_path.replace('.csv','_events_per_second.csv'), events_per_second_per_bin, fmt='%1.2f', delimiter=',', newline='\n')


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
    ################# done calculating events per lap #############################
    ###############################################################################



    ###############################################################################
    ########################## apply gaussian filter ##############################
    ###############################################################################

    gaussian_filtered_events_per_second = np.zeros((total_number_of_cells,total_number_of_time_bins_in_all_env),dtype='float')

    #apply a one dimensional gaussian filter to event data for each cell:
    for env in range (0,number_of_environments):
        gaussian_filtered_event_data_in_this_env = ndimage.gaussian_filter1d(events_per_second_per_bin[:,env_starts_at_this_bin[env]:env_starts_at_this_bin[env+1]],sigma=gaussian_filter_sigma,axis=1)
        #gaussian_filtered_event_data_in_this_env = ndimage.gaussian_filter1d(events_per_lap[:,env_starts_at_this_bin[env]:env_starts_at_this_bin[env+1]],sigma=gaussian_filter_sigma,axis=1)
        
        for cell in range(0,gaussian_filtered_event_data_in_this_env.shape[0]): 
            for env_bin in range(0,gaussian_filtered_event_data_in_this_env.shape[1]):
                gaussian_filtered_events_per_second[cell][env_bin + env_starts_at_this_bin[env]] = gaussian_filtered_event_data_in_this_env[cell][env_bin]
        
    #gaussian_filtered_events_per_second = ndimage.gaussian_filter1d(events_per_second_per_bin,sigma=gaussian_filter_sigma,axis=1)        
#    np.savetxt(file_path.replace('.csv','_gaussian_filter_events_per_second.csv'), gaussian_filtered_events_per_second, fmt='%f', delimiter=',', newline='\n') 

    ###############################################################################
    ##################### done applying gaussian filter ###########################
    ###############################################################################



    ###############################################################################
    ############ generate ranking for cells according to max response #############
    ###############################################################################

    place_data_each_cell = np.zeros((total_number_of_cells,total_number_of_time_bins_in_all_env+2*number_of_environments),dtype='float')
        
    for cell in range(0,total_number_of_cells): 
        cell_max_response = np.max(gaussian_filtered_events_per_second[cell,:])
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
    generate_plots(file_path, place_data_each_cell,number_of_environments, laps_in_environment, total_number_of_cells, bins_in_environment, env_starts_at_this_bin,env_track_lengths,odor_sequence_in_letters,distance_bin_size,odor_start_and_end_points,speed_threshold,total_number_distance_bins_in_all_env,gaussian_filter_sigma,lower_threshold_for_activity,time_bin_size,number_of_time_bins)

    ###############################################################################
    ####### done generating ranking for cells according to max response ###########
    ###############################################################################


    ###############################################################################
    ###############################################################################
    ###################### now we plot some good nice heatmaps ####################
    ###############################################################################
    ###############################################################################
#based on source: http://stackoverflow.com/questions/14391959/heatmap-in-matplotlib-with-pcolor
def generate_plots(file_path, place_field_events_each_cell,number_of_environments, laps_in_environment, total_number_of_cells, bins_in_environment, env_starts_at_this_bin,env_track_lengths,odor_sequence,distance_bin_size,odor_start_and_end_points,speed_threshold,total_number_distance_bins_in_all_env,gaussian_filter_sigma,lower_threshold_for_activity,time_bin_size,number_of_time_bins):

    figs = []

    #heatmap_colors = ['Blues','Greens','BuPu','Oranges','Purples','Reds','RdPu','PuBu']
    #use a different plot legend color for each environment
    #plot_color = ['r','b','g','m','c','y']  
    plot_color = ['r','r','r','r','r','r']  

    
    for plot_env in range (0,number_of_environments):
        data_array_all = place_field_events_each_cell[np.argsort(place_field_events_each_cell[:,plot_env*2],kind='quicksort')]
        
        data_array = []
        for row in range(0,data_array_all.shape[0]):
            if(data_array_all[row][2*plot_env] >= 0 and data_array_all[row][2*plot_env+1]>=lower_threshold_for_activity):
                if(len(data_array) == 0):
                    data_array = data_array_all[row,:]
                else:
                    data_array = np.vstack([data_array, data_array_all[row,:]])
        
        if(len(data_array) == 0):
            data_array = np.zeros((2,data_array_all.shape[1]))
        elif(len(data_array) == data_array_all.shape[1]):
            data_array = np.vstack([np.zeros((1,data_array_all.shape[1])),data_array])            
        
        #np.savetxt(file_path.replace('.csv','_plotted_data_sorted_for_env_%d.csv'%plot_env), data_array[:,0:2*number_of_environments], fmt='%f', delimiter=',', newline='\n')   

        #for env in range (plot_env,plot_env+1):
        for env in range (0,number_of_environments):
            fig = plt.figure()
            fig.subplots_adjust(hspace=0)
            fig.set_rasterized(True)
            fig.suptitle('Env %d cell activity temporal sequence plotted against Env %d' %(env+1,plot_env+1))            
            
#            if(env+1 == 1 or env+1 == 2):
#                fig.suptitle('Env %d(earlier trials) plotted against env %d' %(env+1,plot_env+1))
#            elif(env+1 == 3 or env+1 == 4):
#                fig.suptitle('Env %d(later trials) plotted against env %d' %(env+1,plot_env+1))

            ax  = plt.subplot2grid((4,4), (0,0), rowspan=4,colspan=4)
            
            #to label the odor sequence on the plots
            od = odor_sequence[env*3:(env+1)*3]            
            sort_od = odor_sequence[plot_env*3:(plot_env+1)*3] 

            plt.figtext(0.84,0.9, "Current environment:",                                  fontsize='xx-small', color=plot_color[plot_env], ha ='left') 
            plt.figtext(0.84,0.85, "%d - %s%s%s"%(env+1,od[0],od[1],od[2]),                fontsize='18', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.8, "Sort reference env:",                                   fontsize='xx-small', color=plot_color[plot_env], ha ='left') 
            plt.figtext(0.84,0.75,"%d - %s%s%s"%(plot_env+1,sort_od[0],sort_od[1],sort_od[2]), fontsize='large', color=plot_color[plot_env], ha ='left')

            plt.figtext(0.84,0.7,"Environments: %d" %number_of_environments,               fontsize='x-small', color=plot_color[plot_env], ha ='left')           
            plt.figtext(0.84,0.65,"Time bins: %d" %number_of_time_bins,                    fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.6,"Bin size: %dms" %time_bin_size,                          fontsize='x-small', color=plot_color[plot_env], ha ='left')            
            plt.figtext(0.84,0.55,"Track: %1.1fm" %(env_track_lengths[env]/1000.0),        fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.5,"Laps: %d" %laps_in_environment[env],                     fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.45,"Cells: %d" %total_number_of_cells,                      fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.4,"min speed: %dmm/s" %speed_threshold,                     fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.35,"Sigma: %1.1f" %gaussian_filter_sigma,                   fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.3,"min.activity: %1.3f" %lower_threshold_for_activity,      fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.25,"Cells in env: %d" %data_array.shape[0],                 fontsize='x-small', color=plot_color[plot_env], ha ='left')

            plt.figtext(0.03,0.15,"%d" %data_array.shape[0],                               fontsize='large', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.02,0.10,"cells",                                                 fontsize='large', color=plot_color[plot_env], ha ='left')
    
            #if(plot_env%2 == 0):
            #heatmap = ax.pcolor(normalized_data_array, cmap=plt.cm.Blues) 
            heatmap = ax.pcolormesh(data_array[:,env_starts_at_this_bin[env]+2*number_of_environments:env_starts_at_this_bin[env+1]+2*number_of_environments], cmap=plt.cm.jet,vmin=0.00,vmax=1.00) 
            color_legend = plt.colorbar(heatmap,aspect=30)
            color_legend.ax.tick_params(labelsize=5) 
            #color_legend.set_label('evets per second')
            plt.figtext(0.765,0.6,'summed events (normalized to max bin)',fontsize='x-small',rotation=90)
            
            ax.xaxis.tick_bottom()
            if(number_of_time_bins == 100 or (env_track_lengths[env] == 4000 and number_of_time_bins == 0)):
                ax.set_xlabel('Time(s)')
                plt.setp(ax,xticklabels=['0s','4s','8s','12s','16s','20s'],visible=True)
            elif(number_of_time_bins == 200 or (env_track_lengths[env] == 8000 and number_of_time_bins == 0)):
                ax.set_xlabel('Time(s)')
                plt.setp(ax,xticklabels=['0s','10s','20s','30s','40s'],visible=True)
            else:
                ax.set_xlabel('Time bins (%d ms each)'%time_bin_size)
                plt.setp(ax.get_xticklabels(),visible=True)
            
            plt.xlim (0,bins_in_environment[env])
            plt.ylim (0,data_array.shape[0]) 
            plt.gca().invert_yaxis()
            

            ax.yaxis.set_major_locator(MaxNLocator(integer=True)) 
            ax.set_ylabel('Cell#')
            fig.add_subplot(ax)
     
            #can be commented out to stop showing all plots in the console
            plt.show()
            figs.append(fig)
#            if (env == plot_env):
#                env_aligned_to_itself_figs.append(fig)                
            plt.close()


    
    if len(figs) > 0:
        pdf_name = file_path.replace("behavior_and_events.csv","temporal_sequence.pdf")
        pp = PdfPages(pdf_name)

        for fig in figs:
                pp.savefig(fig,dpi=300,edgecolor='r')
        pp.close()

        #figs_to_be_saved = [1,0,1,0,0,1,0,1,0,0,0,0,0,0,0,0]     
        #figs_to_be_saved = [1,0,1,0,0,1,0,1,1,0,1,0,0,1,0,1] #more figure comparisons    
        #figs_to_be_saved = [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0]  #when there is just one starting environment
        #figs_to_be_saved = [1,0,1,0,0,0,1,0,1,0,0,0,0,0,0,0]  #when there is just one starting environment, more comparisons        
#        for fig in range(0,len(figs)):
#            if(figs_to_be_saved[fig] == 1):            
#                pp.savefig(figs[fig],dpi=300,edgecolor='r')
#        pp.close()

###############################################################################

main()