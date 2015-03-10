#http://stackoverflow.com/questions/27578648/customizing-colors-in-matplotlib-heatmap

import matplotlib.pyplot as plt
#from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import numpy as np
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_pdf import PdfPages
import os
import re
from scipy import ndimage
#import math

def read_data_and_generate_plots(file_path,odor_response_time_window, distance_bin_size,speed_threshold,gaussian_filter_sigma,lower_threshold_for_activity):
    
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
    
    #time_stamp = event_data[1,:]

    odor = event_data[2,:]
    lap_count = event_data[6,:]
    total_laps = max(lap_count) + 1
    print 'Number of laps = %d' %total_laps
    
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
    
    
    


        
        
    #find out the odor sequence for each environment
    #this is to print the correct odor sequence on the x-axis
    #and find out the track length in each environment 
      
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
        bins_in_environment[env] = env_track_lengths[env] / distance_bin_size
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


    total_number_distance_bins_in_all_env = np.sum(bins_in_environment)
    
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

    
    ###############################################################################    
    ###############################################################################
    ####################### calculate total events per bin ########################
    ###############################################################################
    
    total_events_per_bin_per_cell = np.zeros((total_number_of_cells,total_number_distance_bins_in_all_env),dtype='float')
    total_time_per_bin = np.zeros(total_number_distance_bins_in_all_env,dtype='float')    
    average_speed_per_bin = np.zeros(total_number_distance_bins_in_all_env,dtype='float')   
    
#    for cell in range(0,total_number_of_cells):    
#        if (cell % 50 == 0):
#            print 'Processing cell# %d / %d'%(cell,total_number_of_cells)    

    #run this while loop until all columns have been checked for the cell in this row
    last_evaluated_bin = -1
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
                    bin_for_current_event = env_starts_at_this_bin[environment[frame]-1] + distance[frame] / distance_bin_size
                    current_bin_total_events = total_events_per_bin_per_cell[cell][bin_for_current_event] + event_data[cell][frame]
                    total_events_per_bin_per_cell[cell][bin_for_current_event] = current_bin_total_events

                #we only need to calculate the total time spent in a bin for one cell (this time has to be same for all cells, here we choose the zeroth cell)
                # 5.0cm is divided by speed to get the time spent in the current bin (speed was calculated as time required to cross each 50mm stretch of the track)
                if (cell == 0 and running_speed[frame] > speed_threshold and (distance[frame] < track_length_in_this_lap)):
                    current_bin = env_starts_at_this_bin[environment[frame]-1] + distance[frame]/distance_bin_size
                    if(last_evaluated_bin != current_bin):
                        last_evaluated_bin = current_bin                   
                        total_time_spent_in_this_bin = total_time_per_bin[current_bin] + 50.0 / running_speed[frame] 
                        total_time_per_bin[current_bin] = total_time_spent_in_this_bin
                        sum_of_speeds = average_speed_per_bin[current_bin] + running_speed[frame]
                        average_speed_per_bin[current_bin] = sum_of_speeds

        elif((distance[frame] >= track_length_in_this_lap) and last_lap_evaluated_for_events < lap_count[frame]):
            have_not_reached_reward_region_in_this_lap = 0
            last_lap_evaluated_for_events = lap_count[frame]
        elif(last_lap_evaluated_for_events < lap_count[frame]):
            have_not_reached_reward_region_in_this_lap = 1
                            


    #np.savetxt(file_path.replace('.csv','_total_events_per_bin.csv'), total_events_per_bin_per_cell, fmt='%i', delimiter=',', newline='\n')                     
    #print total_time_per_bin
    print 'Total running time: %1.1f seconds'%np.sum(total_time_per_bin)

    for current_bin in range(0,total_number_distance_bins_in_all_env):
        environment_in_this_bin = 0
        for env in range(0,number_of_environments-1):
            if(current_bin >= env_starts_at_this_bin[env] and current_bin < env_starts_at_this_bin[env+1]):
                environment_in_this_bin = env  
        average_speed_in_current_bin = average_speed_per_bin[current_bin] / laps_in_environment[environment_in_this_bin]
        average_speed_per_bin[current_bin] = average_speed_in_current_bin
    
    print average_speed_per_bin

    ###############################################################################
    ########################calculate events per lap ##############################
    ###############################################################################

    events_per_second_per_bin = np.zeros((total_number_of_cells,total_number_distance_bins_in_all_env),dtype='float') 
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

    gaussian_filtered_events_per_second = np.zeros((total_number_of_cells,total_number_distance_bins_in_all_env),dtype='float')

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

    place_data_each_cell = np.zeros((total_number_of_cells,total_number_distance_bins_in_all_env+2*number_of_environments),dtype='float')
        
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
    generate_plots(file_path, place_data_each_cell,total_time_per_bin,number_of_environments, laps_in_environment, total_number_of_cells, bins_in_environment, env_starts_at_this_bin,env_track_lengths,odor_sequence_in_letters,distance_bin_size,odor_start_and_end_points,speed_threshold,total_number_distance_bins_in_all_env,gaussian_filter_sigma,lower_threshold_for_activity,average_speed_per_bin)

    ###############################################################################
    ########################done generating data for plots ########################
    ###############################################################################


###############################################################################
###############################################################################
###################### now we plot some good nice heatmaps ####################
###############################################################################
###############################################################################
#based on source: http://stackoverflow.com/questions/14391959/heatmap-in-matplotlib-with-pcolor
def generate_plots(file_path, place_field_events_each_cell,total_time_per_bin,number_of_environments, laps_in_environment, total_number_of_cells, bins_in_environment, env_starts_at_this_bin,env_track_lengths,odor_sequence,distance_bin_size,odor_start_and_end_points,speed_threshold,total_number_distance_bins_in_all_env,gaussian_filter_sigma,lower_threshold_for_activity,average_speed_per_bin):

    figs = []
#    env_aligned_to_itself_figs = []


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
            fig.suptitle('Env %d place cell activity plotted against Env %d' %(env+1,plot_env+1))            
            
#            if(env+1 == 1 or env+1 == 2):
#                fig.suptitle('Env %d(earlier trials) plotted against env %d' %(env+1,plot_env+1))
#            elif(env+1 == 3 or env+1 == 4):
#                fig.suptitle('Env %d(later trials) plotted against env %d' %(env+1,plot_env+1))

            ax  = plt.subplot2grid((4,4), (0,0), rowspan=4,colspan=4)
            
            #to label the odor sequence on the plots
            od = odor_sequence[env*3:(env+1)*3]            
            sort_od = odor_sequence[plot_env*3:(plot_env+1)*3] 

            plt.figtext(0.32,0.91, "%s"%od[0], fontsize='large', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.46,0.91, "%s"%od[1], fontsize='large', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.60,0.91, "%s"%od[2], fontsize='large', color=plot_color[plot_env], ha ='left')            

            plt.figtext(0.84,0.9, "Current environment:",                                  fontsize='xx-small', color=plot_color[plot_env], ha ='left') 
            plt.figtext(0.84,0.85, "%d - %s%s%s"%(env+1,od[0],od[1],od[2]),                fontsize='18', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.8, "Sort reference env:",                                   fontsize='xx-small', color=plot_color[plot_env], ha ='left') 
            plt.figtext(0.84,0.75, "%d - %s%s%s"%(plot_env+1,sort_od[0],sort_od[1],sort_od[2]), fontsize='large', color=plot_color[plot_env], ha ='left')

            plt.figtext(0.84,0.7,"Environments: %d" %number_of_environments,               fontsize='x-small', color=plot_color[plot_env], ha ='left')           
            plt.figtext(0.84,0.65,"Bin size: %dmm" %distance_bin_size,                     fontsize='x-small', color=plot_color[plot_env], ha ='left')            
            plt.figtext(0.84,0.6,"Track: %1.1fm" %(env_track_lengths[env]/1000.0),         fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.55,"Laps: %d" %laps_in_environment[env],                    fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.5,"Cells: %d" %total_number_of_cells,                       fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.45,"min speed: %dmm/s" %speed_threshold,                    fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.4,"Sigma: %1.1f" %gaussian_filter_sigma,                    fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.35,"min.activity: %1.3f" %lower_threshold_for_activity,     fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.84,0.3,"Cells in env: %d" %data_array.shape[0],                  fontsize='x-small', color=plot_color[plot_env], ha ='left')

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
            if(env_track_lengths[env] == 4000):
                ax.set_xlabel('Distance(m)')
                plt.setp(ax,xticklabels=['0','0.5','1','1.5','2','2.5','3','3.5','4'],visible=True)
            elif(env_track_lengths[env] == 8000):
                ax.set_xlabel('Distance(m)')
                plt.setp(ax,xticklabels=['0','1','2','3','4','5','6','7','8'],visible=True)
            else:
                ax.set_xlabel('Distance bin (%d mm each)'%distance_bin_size)
                plt.setp(ax.get_xticklabels(),visible=True)

            
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


    for env in range (0,number_of_environments):
        fig = plt.figure()
        fig.subplots_adjust(hspace=0)
        fig.set_rasterized(True)
        fig.suptitle('Env %d average speed (normalized to max average speed)' %(env+1)) 

        this_env_average_speed_per_bin = average_speed_per_bin[env_starts_at_this_bin[env]:env_starts_at_this_bin[env+1]]
        #np.savetxt(file_path.replace('.csv','_histogram_heights.csv'), histogram_heights, fmt='%i', delimiter=',', newline='\n')  
        
        max_average_speed = max(average_speed_per_bin)
        #max_time_per_bin = max(total_time_per_bin)
        normalized_average_speed = [(x / max_average_speed) for x in this_env_average_speed_per_bin]
        #print histogram_heights
        #print normalized_total_time_per_bin
        
        ax1 = plt.subplot2grid((4,4), (0,0), rowspan=4,colspan=4)
        #plt.bar(range(bins_in_environment[env]),histogram_heights, width=1, color='g',linewidth=0)
        plt.plot(range(bins_in_environment[env]),normalized_average_speed,'r-', linewidth = 0.1)
        #ax1.set_xlabel('Distance bin (%d mm each)'%distance_bin_size)
        ax1.set_ylabel('Normalized Average Speed',fontsize='large')
        #ax1.set_ylim(0,1)
        plt.setp(ax1.get_yticklabels(),visible=True)

        ax1.xaxis.tick_bottom()
        if(env_track_lengths[env] == 4000):
            ax1.set_xlabel('Distance(m)')
            plt.setp(ax1,xticklabels=['0','0.5','1','1.5','2','2.5','3','3.5','4'],visible=True)
        elif(env_track_lengths[env] == 8000):
            ax1.set_xlabel('Distance(m)')
            plt.setp(ax1,xticklabels=['0','1','2','3','4','5','6','7','8'],visible=True)
        else:
            ax1.set_xlabel('Distance bin (%d mm each)'%distance_bin_size)
            plt.setp(ax1.get_xticklabels(),visible=True)

        #to label the odor sequence on the plots
        od = odor_sequence[env*3:(env+1)*3] 
        plt.figtext(0.35,0.91, "%s"%od[0], fontsize='large', color=plot_color[plot_env], ha ='left')
        plt.figtext(0.55,0.91, "%s"%od[1], fontsize='large', color=plot_color[plot_env], ha ='left')
        plt.figtext(0.75,0.91, "%s"%od[2], fontsize='large', color=plot_color[plot_env], ha ='left') 
        
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

    
    if len(figs) > 0:
        pdf_name = file_path.replace("behavior_and_events.csv","place_cells_based_on_gaussian_filtered_events_per_second.pdf")
#        pdf_name = file_path.replace(".csv","_time_normalized_place_cells.pdf")
        pp = PdfPages(pdf_name)
#        for fig in env_aligned_to_itself_figs:
#            pp.savefig(fig,dpi=300,edgecolor='r')

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


#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

def main():
    #for PC, the format is something like: directory_path ='C:/Users/axel/Desktop/test_data'
    directory_path ='/Users/njoshi/Desktop/events_test'
    odor_response_time_window = 2000 #time in ms
    distance_bin_size = 50 #distance bin in mm
    speed_threshold = 50 #minimum speed in mm/s for selecting events
    gaussian_filter_sigma = 2.00
    lower_threshold_for_activity = 0.20
    #env_track_lengths = [4000,4000,4000,4000]
    #odor_response_distance_window = 500 #in mm
    
    file_names = [os.path.join(directory_path, f)
        for dirpath, dirnames, files in os.walk(directory_path)
        for f in files if f.endswith('.csv')]
    file_names.sort(key=natural_key)
    
    for mouse_data in file_names:
        print 'Analyzing this file: '+ mouse_data
#        if os.path.isfile(mouse_data.replace(".csv","_sorted_place_cells.pdf")):
#            print 'A pdf already exists for this file. Delete the pdf to generate a new one.'
#        else:
        read_data_and_generate_plots(mouse_data,odor_response_time_window, distance_bin_size,speed_threshold,gaussian_filter_sigma,lower_threshold_for_activity)

main()