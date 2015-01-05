import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import os
import re

def read_data_and_generate_plots(file_path,odor_response_time_window, distance_bin_size):
    
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
    #row 8 = time stamp generated by Incopix imaging software, probably will never be used
    #row 9 to last row = event data for cells in this recording
    
    #time_stamp = event_data[1,:]
    odor = event_data[2,:]
    lap_count = event_data[6,:]
    total_laps = max(lap_count) + 1
    
    distance = event_data[5,:]
    
    environment = event_data[7,:]
    number_of_environments = max(environment)
    print 'Number of laps = %d' %total_laps
    print 'Number of environments = %d' %number_of_environments
    #print odor[0:15]
    
    
    #delete the desired number of rows/columns in the desired axis
    event_data = np.delete(event_data, (0,1,2,3,4,5,6,7), axis=0)
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
        if(environment[column] > environment[column-1]):
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
    env_starts_at_this_bin = np.zeros(number_of_environments+1,dtype='int')
    total_number_distance_bins_in_all_env = 0
    
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
        env_starts_at_this_bin[env+1] = env_starts_at_this_bin[env] + ((expansion_factor*4500)/distance_bin_size)
        total_number_distance_bins_in_all_env = total_number_distance_bins_in_all_env + ((expansion_factor*4500)/distance_bin_size)
        
        odor_start_points[env*5 + 0] =  250*expansion_factor
        odor_start_points[env*5 + 1] = 1250*expansion_factor
        odor_start_points[env*5 + 2] = 2250*expansion_factor
        odor_start_points[env*5 + 3] = 3250*expansion_factor
        odor_start_points[env*5 + 4] = 3750*expansion_factor #this is where the odor starts
        

    print 'The odors were presented in this sequence (4 odors per environment):'
    print odor_sequence
    print 'The track lengths in all enviornments are:'
    print environment_track_lengths
    print 'Number of laps in each enviornment:'
    print laps_in_environment
    print 'The odors start at these distance points:'
    print odor_start_points
    print 'New environment starts at bin:'
    print env_starts_at_this_bin
    print 'Total number of distance bins in all enviornments: %d'%total_number_distance_bins_in_all_env
    
    ###############################################################################
    ###### add the events in response to each odor in each lap
    ###############################################################################
    
    event_data_per_bin = np.empty((total_number_of_cells,total_number_distance_bins_in_all_env),dtype='int') 
    
    for cell in range(0,total_number_of_cells):    
        if (cell % 50 == 0):
            print 'Processing cell# %d / %d'%(cell,total_number_of_cells)    
        
        #last_frame_bin = 0
        #run thi while loop until all columns have been checked for the cell in this row
        for frame in range(0,total_number_of_frames):
            frame_bin = distance[frame] / distance_bin_size
            #frame_lap = lap_count[frame]
            frame_environment = environment[frame]
            
            insert_event_in_bin = env_starts_at_this_bin[frame_environment-1] + frame_bin
            
            current_bin_total_events = event_data_per_bin[cell][insert_event_in_bin] + event_data[cell][frame]
            event_data_per_bin[cell][insert_event_in_bin] = current_bin_total_events
            
#            last_frame_bin = frame_bin
#            if (frame_lap == 13 and cell == 0 and last_frame_bin != frame_bin):
#                print 'env %d insert bin %d'%(frame_environment,insert_event_in_bin)
#            last_frame_bin = frame_bin
            
#    ###############################################################################
#    ###### calculate the proportion of laps for each odor that had an event #######
#                  # also account for different environments #
#    ###############################################################################
#    
#    event_data_averaged_per_environment = np.empty((total_number_of_cells,total_number_distance_bins_in_all_env),dtype='int')
#    
#    for env in range(0,number_of_environments):
#        environment_start_lap = environment_transitions[env]
#        environment_end_lap = environment_transitions[env+1]
#        environment_lap_count = environment_end_lap - environment_start_lap
#        for row in range(0,event_data_averaged_per_environment.shape[0]):
#            for column in range(env*5,(env+1)*5):
#                laps_with_events = 0
#                for lap in range (environment_start_lap,environment_end_lap):
#                    if(event_data_per_bin[row][env_starts_at_this_bin[current_env] + current_bin_start/distance_bin_size] > 0):
#                        laps_with_events = laps_with_events + 1
#                event_data_averaged_per_environment[row][column] = ((laps_with_events*100) / environment_lap_count)
#    
#    print 'Sample of summed event values'     
#    print event_data_averaged_per_environment[0,:]
    

    
    ###############################################################################
    ################# just a final touch of the magic wand ########################
    ###############################################################################
    generate_plots(file_path, event_data_per_bin,number_of_environments, laps_in_environment, total_number_of_cells, env_starts_at_this_bin,environment_track_lengths,distance_bin_size )


###############################################################################
###############################################################################
###################### now we plot some good nice heatmaps ####################
###############################################################################
###############################################################################
#based on source: http://stackoverflow.com/questions/14391959/heatmap-in-matplotlib-with-pcolor
def generate_plots(file_path, data_array,number_of_environments, laps_in_environment, total_number_of_cells, env_starts_at_this_bin,environment_track_lengths,distance_bin_size):

    figs = []

    #data_array = complete_data_array[np.argsort(complete_data_array[:,odor],kind='quicksort')]
    
    for env in range (0,number_of_environments):

        fig = plt.figure()
        fig.set_rasterized(True)
        fig.suptitle('Place cell activity for %d cells in environment %d' %(total_number_of_cells,env))
        #fig.set_size_inches(10,2) 
        
        #odor_response_ticks = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]

             
        ax = plt.subplot(111)
        heatmap = ax.pcolor(data_array[:,env_starts_at_this_bin[env]:env_starts_at_this_bin[env+1]], cmap=plt.cm.Blues) 
        color_legend = plt.colorbar(heatmap,aspect=30)
        color_legend.ax.tick_params(labelsize=5) 
        #plt.setp(ax.get_yticklabels(), visible=False)
        ax.set_title('%1.1fm track x %d laps'%(environment_track_lengths[env]/1000.00,laps_in_environment[env]), fontsize='x-small')
        ax.set_xlabel('Distance bin (%d mm each)'%distance_bin_size)
        #od = odor_sequence[env*4:(env+1)*4]
        #row_labels = list('%d%d%d%dR' %(od[0],od[1],od[2],od[3]))
        #ax.set_xticklabels(row_labels, minor=False,ha='center')
        ax.xaxis.tick_bottom() 
        plt.ylim (0,total_number_of_cells) 

        plt.setp(ax.get_yticklabels(), visible=True)
        ax.set_ylabel('Cell#')
        fig.add_subplot(ax)
    
        #can be commented out to stop showing all plots in the console
        plt.show()

        figs.append(fig)
        plt.close()
        
    if len(figs) > 0:
        pdf_name = file_path.replace(".csv","_bin_%dmm.pdf"%distance_bin_size)
        pp = PdfPages(pdf_name)
        for fig in figs:
            pp.savefig(fig,dpi=300)
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
    #odor_response_distance_window = 500 #in mm
    
    file_names = [os.path.join(directory_path, f)
        for dirpath, dirnames, files in os.walk(directory_path)
        for f in files if f.endswith('.csv')]
    file_names.sort(key=natural_key)
    
    for mouse_data in file_names:
        print 'Analyzing this file: '+ mouse_data
        if os.path.isfile(mouse_data.replace(".csv","_bin_%dmm.pdf"%distance_bin_size)):
            print 'A pdf already exists for this file. Delete the pdf to generate a new one.'
        else:
            read_data_and_generate_plots(mouse_data,odor_response_time_window, distance_bin_size)

main()