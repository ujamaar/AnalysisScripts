#http://stackoverflow.com/questions/27578648/customizing-colors-in-matplotlib-heatmap

import matplotlib.pyplot as plt
#from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import numpy as np
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_pdf import PdfPages
import os
import re
from scipy import ndimage
import math

def read_data_and_generate_plots(file_path,odor_response_time_window, distance_bin_size,speed_threshold,gaussian_filter_sigma,lower_threshold_for_activity):
    
    event_data = np.loadtxt(file_path, dtype='float', delimiter=',')
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

    odor = [int(x) for x in event_data[2,:]]
    lap_count = [int(x) for x in event_data[6,:]]
    total_laps = max(lap_count) + 1
    
    distance = [int(x) for x in event_data[5,:]]
    
    environment = [int(x) for x in event_data[7,:]]
    number_of_environments = max(environment)
    print 'Number of laps = %d' %total_laps
    print 'Number of environments = %d' %number_of_environments
    #print odor[0:15]
    
    running_speed = event_data[8,:]
    print 'Maximum speed was: %f' %max(running_speed)    
    print 'Minimum speed was: %f' %min(running_speed)
    #np.savetxt(file_path.replace('.csv','_speed_per_bin.csv'), running_speed, fmt='%f', delimiter=',', newline='\n')
    #delete the desired number of rows/columns in the desired axis
    event_data = np.delete(event_data, (0,1,2,3,4,5,6,7,8), axis=0)
    total_number_of_cells = event_data.shape[0]
    print 'Number of cells = %d' %total_number_of_cells
    total_number_of_frames = event_data.shape[1]
    print 'Number of imaging frames: %d'%total_number_of_frames
    
    #print a portion of the event data just to check
    #print event_data[0:10,0:10]
    
    ###############################################################################
    ## extract some parameters: enviorment transitions, odor sequence, track length
    ###############################################################################
    
    #odor_response_time_window = 2000 #time in ms
    #odor_response_distance_window = 500 #in mm
    
    #find out in which laps a new environment starts
    environment_transitions = [0]
    
    for column in range(1,total_number_of_frames):
        if(environment[column] != environment[column-1]):
            environment_transitions.append(lap_count[column])
    
    environment_transitions.append(lap_count[total_number_of_frames-1]+1)
    print 'A new environment starts in these laps:'
    print environment_transitions
    
        
    #find out the odor sequence for each environment
    #this is to print the correct odor sequence on the x-axis
    #and find out the track length in each environment 
      
    odor_sequence = np.zeros((number_of_environments*4),dtype='int')
    odor_start_points = np.zeros((number_of_environments*5),dtype='int')   # 5 instead of 4 b/c we want to include the response to rewards as well
    environment_track_lengths = np.zeros((number_of_environments),dtype='int')
    laps_in_environment = np.zeros(number_of_environments,dtype='int')
    bins_in_environment = np.zeros(number_of_environments,dtype='int')
    env_starts_at_this_bin = np.zeros(number_of_environments+1,dtype='int')
    total_number_distance_bins_in_all_env = 0
    expansion_factor = 0
    
    for env in range(0,number_of_environments):
        current_odor_position = 0
        track_length_in_this_env = 0
        for column in range(1,total_number_of_frames):
            if(lap_count[column] == environment_transitions[env]): #look at first lap of the new environment
                if(odor[column] > odor[column-1]):                 #find when an odor turns on
                    if(int(odor[column]) != odor_sequence[env*4+current_odor_position-1]): #don't repeat the last odor
                        odor_sequence[env*4+current_odor_position] = int(odor[column])  #save this odor in the sequence
                        current_odor_position = current_odor_position+1
                
                #find out the largest distance measurement
                if(distance[column] > track_length_in_this_env):
                    track_length_in_this_env = distance[column]
        expansion_factor = (track_length_in_this_env / 4500) + 1
        environment_track_lengths[env] = expansion_factor*4500
        laps_in_environment[env] = environment_transitions[env+1]-environment_transitions[env]
        bins_in_environment[env] = int(math.ceil((expansion_factor*4500.00)/distance_bin_size))
        env_starts_at_this_bin[env+1] = env_starts_at_this_bin[env] + bins_in_environment[env]

        
        odor_start_points[env*5 + 0] =  250*expansion_factor
        odor_start_points[env*5 + 1] = 1250*expansion_factor
        odor_start_points[env*5 + 2] = 2250*expansion_factor
        odor_start_points[env*5 + 3] = 3250*expansion_factor
        odor_start_points[env*5 + 4] = 3750*expansion_factor #this is where the odor starts

    total_number_distance_bins_in_all_env = np.sum(bins_in_environment)
    
    print 'The odor numbers (4 odors per environment):'
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
 
            
    print 'The odors were presented in this sequence (4 odors per environment):'
    print odor_sequence_in_letters
    print 'The track lengths in all enviornments are:'
    print environment_track_lengths
    print 'Number of laps in each enviornment:'
    print laps_in_environment
    print 'Number of bins in each enviornment:'    
    print bins_in_environment
    print 'The odors start at these distance points:'
    print odor_start_points
    print 'New environment starts at bin:'
    print env_starts_at_this_bin
    print 'Total number of distance bins in all enviornments: %d'%total_number_distance_bins_in_all_env

    ###############################################################################
    ###############################################################################    
    ###############################################################################
    ###### add the events in response to each odor in each lap
    ###############################################################################
    
    total_events_per_bin_per_cell = np.zeros((total_number_of_cells,total_number_distance_bins_in_all_env),dtype='float')
    total_time_per_bin = np.zeros(total_number_distance_bins_in_all_env,dtype='float')    
    
    for cell in range(0,total_number_of_cells):    
        if (cell % 50 == 0):
            print 'Processing cell# %d / %d'%(cell,total_number_of_cells)    

        #run thi while loop until all columns have been checked for the cell in this row
        last_evaluated_bin = -1
        for frame in range(0,total_number_of_frames):
            #events get counted and summed in each bin only if the mouse is running above a threshold speed at the moment (e.g. 10cm/s in this case)
            if (event_data[cell][frame] > 0 and running_speed[frame] > speed_threshold and (distance[frame]/distance_bin_size < odor_start_points[(environment[frame]-1)*5+4]/distance_bin_size)):
                bin_for_current_event = env_starts_at_this_bin[environment[frame]-1] + distance[frame] / distance_bin_size
                current_bin_total_events = total_events_per_bin_per_cell[cell][bin_for_current_event] + event_data[cell][frame]
                total_events_per_bin_per_cell[cell][bin_for_current_event] = current_bin_total_events
                
            #we only need to calculate the total time spent in a bin for one cell (this time has to be same for all cells, here we choose the zeroth cell)
            # 5.0cm is divided by speed to get the time spent in the current bin (speed was calculated as time required to cross each 50mm stretch of the track)
            if (cell == 0 and running_speed[frame] > speed_threshold and (distance[frame]/distance_bin_size < odor_start_points[(environment[frame]-1)*5+4]/distance_bin_size)):
                current_bin = env_starts_at_this_bin[environment[frame]-1] + distance[frame]/distance_bin_size
                if(last_evaluated_bin != current_bin):
                    last_evaluated_bin = current_bin
                    #if(current_bin > 135):
                    #print current_bin                    
                    total_time_spent_in_this_bin = total_time_per_bin[current_bin] + 50.0 / running_speed[frame] 
                    total_time_per_bin[current_bin] = total_time_spent_in_this_bin
                    
    #print total_time_per_bin
    print 'Total running time: %1.1f seconds'%np.sum(total_time_per_bin)

    #np.savetxt(file_path.replace('.csv','_event_data.csv'), total_events_per_bin_per_cell, fmt='%1.2f', delimiter=',', newline='\n') 

    events_per_second_per_bin = np.zeros((total_number_of_cells,total_number_distance_bins_in_all_env),dtype='float') 
    for cell in range(0,total_number_of_cells): 
        for env_bin in range(0,total_number_distance_bins_in_all_env):
            if(total_time_per_bin[env_bin] > 1.00):
                #if(total_events_per_bin_per_cell[cell][env_bin] / total_time_per_bin[env_bin] > lower_threshold_for_activity):
                events_per_second_per_bin[cell][env_bin] = total_events_per_bin_per_cell[cell][env_bin] / total_time_per_bin[env_bin]
            else:
                events_per_second_per_bin[cell][env_bin] = 0.00

    #np.savetxt(file_path.replace('.csv','_events_per_second_per_bin.csv'), events_per_second_per_bin, fmt='%f', delimiter=',', newline='\n')

    #apply a one dimensional gaussian filter to event data for each cell:
    gaussian_filtered_event_data = ndimage.gaussian_filter1d(events_per_second_per_bin,sigma=gaussian_filter_sigma,axis=1)
    #np.savetxt(file_path.replace('.csv','_gaussian_filter_events_per_second_per_bin.csv'), gaussian_filtered_event_data, fmt='%f', delimiter=',', newline='\n') 

#    #to set a lower (or upper) threshold on the data points that actually get plotted
#    gaussian_filtered_event_data_with_threshold = np.zeros((total_number_of_cells,total_number_distance_bins_in_all_env),dtype='float')
#    for row in range(0,total_number_of_cells):
#        for env in range(0,number_of_environments):
#            for env_column in range(env_starts_at_this_bin[env],env_starts_at_this_bin[env] + odor_start_points[env*5+4]/distance_bin_size):
#                if(gaussian_filtered_event_data[row][env_column] >= lower_threshold_for_activity):
#                    gaussian_filtered_event_data_with_threshold[row][env_column] = gaussian_filtered_event_data[row][env_column]

    place_data_each_cell = np.zeros((total_number_of_cells,total_number_distance_bins_in_all_env+2*number_of_environments),dtype='float')
        
    for cell in range(0,total_number_of_cells): 
        cell_max_response = np.max(gaussian_filtered_event_data[cell,:])
        for env in range(0,number_of_environments):
            env_max_response_column = 0
            env_max_response = 0.00
            for env_bin in range(env_starts_at_this_bin[env],env_starts_at_this_bin[env+1]):
                if (gaussian_filtered_event_data[cell][env_bin] > env_max_response):
                    env_max_response_column = env_bin
                    env_max_response = gaussian_filtered_event_data[cell][env_bin] 
            if(env_max_response_column == 0 and env_max_response == 0.00):
                place_data_each_cell[cell][2*env]= -1
                place_data_each_cell[cell][2*env+1]= env_max_response
            elif(cell_max_response >= lower_threshold_for_activity):
                place_data_each_cell[cell][2*env]= env_max_response_column
                place_data_each_cell[cell][2*env+1]= env_max_response                
                
                for column in range(2*number_of_environments + env_starts_at_this_bin[env],2*number_of_environments + env_starts_at_this_bin[env] + odor_start_points[env*5+4]/distance_bin_size):
                    #if(env_max_response > lower_threshold_for_activity):
                    place_data_each_cell[cell][column] = gaussian_filtered_event_data[cell][column-2*number_of_environments] / cell_max_response

    #np.savetxt(file_path.replace('.csv','_gaussian_filter_events_per_second_per_bin_and_ranking_by_peak.csv'), place_data_each_cell, fmt='%f', delimiter=',', newline='\n')            
    #now send the data for plotting:
    generate_plots(file_path, place_data_each_cell,total_time_per_bin,number_of_environments, laps_in_environment, total_number_of_cells, bins_in_environment, env_starts_at_this_bin,environment_track_lengths,odor_sequence_in_letters,distance_bin_size,odor_start_points,expansion_factor,speed_threshold,total_number_distance_bins_in_all_env,gaussian_filter_sigma,lower_threshold_for_activity)


###############################################################################
###############################################################################
###################### now we plot some good nice heatmaps ####################
###############################################################################
###############################################################################
#based on source: http://stackoverflow.com/questions/14391959/heatmap-in-matplotlib-with-pcolor
def generate_plots(file_path, place_field_events_each_cell,total_time_per_bin,number_of_environments, laps_in_environment, total_number_of_cells, bins_in_environment, env_starts_at_this_bin,environment_track_lengths,odor_sequence,distance_bin_size,odor_start_points,expansion_factor,speed_threshold,total_number_distance_bins_in_all_env,gaussian_filter_sigma,lower_threshold_for_activity):

    figs = []
    env_aligned_to_itself_figs = []

    #to plot the hitogram of summed events
    #all_histogram_heights = np.sum(place_field_events_each_cell[:,2*number_of_environments:place_field_events_each_cell.shape[1]], axis=0)


    #heatmap_colors = ['Blues','Greens','BuPu','Oranges','Purples','Reds','RdPu','PuBu']
    #use a different plot legend color for each environment
    plot_color = ['r','b','g','m','c','y']  
    
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
            fig.suptitle('Environment %d place cell activity sorted according to environment %d' %(env+1,plot_env+1))

            ax  = plt.subplot2grid((4,4), (0,0), rowspan=4,colspan=4)
            
            #to label the odor sequence on the plots
            od = odor_sequence[env*4:(env+1)*4]            
            sort_od = odor_sequence[plot_env*4:(plot_env+1)*4] 

            plt.figtext(0.2 ,0.91, "%s"%od[0], fontsize='large', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.33,0.91, "%s"%od[1], fontsize='large', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.47,0.91, "%s"%od[2], fontsize='large', color=plot_color[plot_env], ha ='left')            
            plt.figtext(0.6 ,0.91, "%s"%od[3], fontsize='large', color=plot_color[plot_env], ha ='left')

            plt.figtext(0.85,0.9, "Current environment:",                                  fontsize='xx-small', color=plot_color[plot_env], ha ='left') 
            plt.figtext(0.85,0.85, "%d - %s%s%s%s"%(env+1,od[0],od[1],od[2],od[3]),        fontsize='large', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.85,0.8, "Sort reference env:",                                   fontsize='xx-small', color=plot_color[plot_env], ha ='left') 
            plt.figtext(0.85,0.75, "%d - %s%s%s%s"%(plot_env+1,sort_od[0],sort_od[1],sort_od[2],sort_od[3]), fontsize='large', color=plot_color[plot_env], ha ='left')

            plt.figtext(0.85,0.7,"Environments: %d" %number_of_environments,               fontsize='x-small', color=plot_color[plot_env], ha ='left')           
            plt.figtext(0.85,0.65,"Bin size: %dmm" %distance_bin_size,                     fontsize='x-small', color=plot_color[plot_env], ha ='left')            
            plt.figtext(0.85,0.6,"Track: %1.1fm" %(environment_track_lengths[env]/1000.0), fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.85,0.55,"Laps: %d" %laps_in_environment[env],                    fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.85,0.5,"Cells: %d" %total_number_of_cells,                       fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.85,0.45,"min speed: %dcm/s" %speed_threshold,                    fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.85,0.4,"Sigma: %1.1f" %gaussian_filter_sigma,                    fontsize='x-small', color=plot_color[plot_env], ha ='left')
            plt.figtext(0.85,0.35,"min activity: %1.2f" %lower_threshold_for_activity,    fontsize='x-small', color=plot_color[plot_env], ha ='left')

            ax.spines['bottom'].set_color(plot_color[plot_env])
            ax.spines['top'   ].set_color(plot_color[plot_env]) 
            ax.spines['right' ].set_color(plot_color[plot_env])
            ax.spines['left'  ].set_color(plot_color[plot_env])
    
            #if(plot_env%2 == 0):
            #heatmap = ax.pcolor(normalized_data_array, cmap=plt.cm.Blues) 
            heatmap = ax.pcolormesh(data_array[:,env_starts_at_this_bin[env]+2*number_of_environments:env_starts_at_this_bin[env+1]+2*number_of_environments], cmap=plt.cm.jet,vmin=0.00,vmax=1.00) 
            color_legend = plt.colorbar(heatmap,aspect=30)
            color_legend.ax.tick_params(labelsize=5) 
            #color_legend.set_label('evets per second')
            plt.figtext(0.765,0.55,'events per second (normalized to max)',fontsize='x-small',rotation=90)
            
            #ax.set_title('%1.1fm track x %d laps     Odor sequence:%s%s%s%s'%(environment_track_lengths[env]/1000.00,laps_in_environment[env],od[0],od[1],od[2],od[3]), fontsize='x-small')
            ax.set_xlabel('Distance bin (%d mm each)'%distance_bin_size)
            ax.xaxis.tick_bottom() 
            plt.setp(ax.get_xticklabels(),visible=True)
            
            plt.xlim (0,bins_in_environment[env])
            plt.ylim (0,data_array.shape[0]) 
            plt.gca().invert_yaxis()
            
            first_cell_with_events = -1
            cell = 0
            while(first_cell_with_events < 0 and cell < data_array.shape[0]):
                if ((data_array[cell][1+plot_env*2]) > 0):
                    first_cell_with_events = cell
                cell = cell+1
            plt.axhline(y=first_cell_with_events, linewidth=0.1, color='k')
            
            #draw white lines to mark odor regions
            plt.axvline(x=odor_start_points[env*5+0]/distance_bin_size, linewidth=0.1, color='w')
            plt.axvline(x=(odor_start_points[env*5+0]+odor_start_points[env*5+0]*3)/distance_bin_size, linewidth=0.1, color='w')
            plt.axvline(x=odor_start_points[env*5+1]/distance_bin_size, linewidth=0.1, color='w')
            plt.axvline(x=(odor_start_points[env*5+1]+odor_start_points[env*5+0]*3)/distance_bin_size, linewidth=0.1, color='w')
            plt.axvline(x=odor_start_points[env*5+2]/distance_bin_size, linewidth=0.1, color='w')
            plt.axvline(x=(odor_start_points[env*5+2]+odor_start_points[env*5+0]*3)/distance_bin_size, linewidth=0.1, color='w')
            plt.axvline(x=odor_start_points[env*5+3]/distance_bin_size, linewidth=0.1, color='w')
            plt.axvline(x=(odor_start_points[env*5+3]+odor_start_points[env*5+0]*3)/distance_bin_size, linewidth=0.1, color='w')
            plt.axvline(x=odor_start_points[env*5+4]/distance_bin_size, linewidth=0.5, color='r')
            #plt.axvspan(odor_start_points[env*5+4]/distance_bin_size, (odor_start_points[env*5+4]+odor_start_points[env*5+0]*3)/distance_bin_size, facecolor='r', alpha=0.1)
                
            #plt.setp(ax.get_yticklabels(), visible=True)

            ax.yaxis.set_major_locator(MaxNLocator(integer=True)) 
            ax.set_ylabel('Cell#')
            fig.add_subplot(ax)
            ###############################################################################
#                            
#            histogram_heights = all_histogram_heights[env_starts_at_this_bin[env]:env_starts_at_this_bin[env+1]]
#            #np.savetxt(file_path.replace('.csv','_histogram_heights.csv'), histogram_heights, fmt='%i', delimiter=',', newline='\n')  
#            
#            max_histogram_height = max(all_histogram_heights)
#            max_time_per_bin = max(total_time_per_bin)
#            normalized_total_time_per_bin = [((x * max_histogram_height)/max_time_per_bin) for x in total_time_per_bin[env_starts_at_this_bin[env]:env_starts_at_this_bin[env+1]]]
#            #print histogram_heights
#            #print normalized_total_time_per_bin
#            
#            ax1 = plt.subplot2grid((4,4), (3,0), rowspan=1,colspan=4,sharex=ax)
#            plt.bar(range(bins_in_environment[env]),histogram_heights, width=1, color='g',linewidth=0)
#            plt.plot(range(bins_in_environment[env]),normalized_total_time_per_bin,'r-', linewidth = 0.1)
#            ax1.set_xlabel('Distance bin (%d mm each)'%distance_bin_size)
#            ax1.set_ylabel('summed events',fontsize='xx-small')
#            ax1.set_ylim(0,max_histogram_height)
#            plt.setp(ax1.get_yticklabels(),visible=False)
#
##            ax1.yaxis.set_major_locator(majorLocator)
##            ax1.yaxis.set_major_formatter(majorFormatter)
##            #ax1.yaxis.set_minor_locator(minorLocator)
#            
#            color_legend = plt.colorbar(heatmap,aspect=30)
#            fig.delaxes(fig.axes[3]) #here axis 0 = plot in ax, 1 = colorbar in ax, 2 = plot in ax1, 3 = heatmap in ax1
#            #draw colored bands for odor regions
#            odor_region_shade = 0.1
#            plt.axvspan(odor_start_points[env*5+0]/distance_bin_size, (odor_start_points[env*5+0]+odor_start_points[env*5+0]*3)/distance_bin_size, facecolor='b', alpha=odor_region_shade)
#            plt.axvspan(odor_start_points[env*5+1]/distance_bin_size, (odor_start_points[env*5+1]+odor_start_points[env*5+0]*3)/distance_bin_size, facecolor='r', alpha=odor_region_shade)
#            plt.axvspan(odor_start_points[env*5+2]/distance_bin_size, (odor_start_points[env*5+2]+odor_start_points[env*5+0]*3)/distance_bin_size, facecolor='g', alpha=odor_region_shade)                    
#            plt.axvspan(odor_start_points[env*5+3]/distance_bin_size, (odor_start_points[env*5+3]+odor_start_points[env*5+0]*3)/distance_bin_size, facecolor='m', alpha=odor_region_shade)
#            plt.axvline(x=odor_start_points[env*5+4]/distance_bin_size, linewidth=0.1, color='b')
# 
#            ax1.spines['bottom'].set_color(plot_color[plot_env])
#            ax1.spines['top'   ].set_color(plot_color[plot_env]) 
#            ax1.spines['right' ].set_color(plot_color[plot_env])
#            ax1.spines['left'  ].set_color(plot_color[plot_env])
#
#            fig.add_subplot(ax1)


   
            #can be commented out to stop showing all plots in the console
            plt.show()
            figs.append(fig)
            if (env == plot_env):
                env_aligned_to_itself_figs.append(fig)                
            plt.close()
        
    if len(figs) > 0:
        pdf_name = file_path.replace(".csv","_time_normalized_place_cells.pdf")
        pp = PdfPages(pdf_name)
        for fig in env_aligned_to_itself_figs:
            pp.savefig(fig,dpi=300,edgecolor='r')
        for fig in figs:
            pp.savefig(fig,dpi=300,edgecolor='r')
        pp.close() 


#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

def main():
    #for PC, the format is something like: directory_path ='C:/Users/axel/Desktop/test_data'
    directory_path ='/Users/njoshi/Desktop/events_test'
    odor_response_time_window = 2000 #time in ms
    distance_bin_size = 50 #distance bin in mm
    speed_threshold = 5 #minimum speed in cm/s for seecting evets
    gaussian_filter_sigma = 2.00
    lower_threshold_for_activity = 0.25
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