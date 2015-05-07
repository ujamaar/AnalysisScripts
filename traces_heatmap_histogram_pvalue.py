import matplotlib.pyplot as plt # needed for plotting graphs
import matplotlib.ticker as ticker #to set custom axis labels
import numpy # needed for various math tasks
from matplotlib.backends.backend_pdf import PdfPages # for saving figures as pdf
import os # needed to find files
import re # needed to arrange filenames alphabetically


def main():
    # specify the various parameters as needed:
    frames_pre_odor_onset = 50 #time in milliseconds
    frames_post_odor_onset = 100 #time in milliseconds

    data_files_directory_path ='/Users/njoshi/Desktop/data_analysis/input_files'
    output_directory_path = '/Users/njoshi/Desktop/data_analysis/output_files'

#    data_files_directory_path  = '/Volumes/walter/Virtual_Odor/imaging_data/wfnjC22'
#    output_directory_path = '/Volumes/walter/Virtual_Odor/analysis'

    replace_previous_versions_of_plots = False  

    #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><#

    #detect all the behavior.csv files in the folder
    file_names = []
    for dirpath, dirnames, files in os.walk(data_files_directory_path):
        for behavior_file in files:
            if behavior_file.endswith('combined_behavior_and_traces.csv'):                
                if(replace_previous_versions_of_plots == True):
                    file_names.append(os.path.join(dirpath, behavior_file))
                else:
                    # to check if there's already a plot for the given file
                    behavior_file_has_already_been_analyzed = False
                    mouse_ID = behavior_file[0:7]
                    mouse_ID_and_date = behavior_file[0:18]
                    for plot_dirpath, plot_dirnames, plot_files in os.walk(output_directory_path + '/' + mouse_ID + '/' + mouse_ID_and_date):                    
                        for plot_file in plot_files:
                            if plot_file.endswith('.pdf'):  
                                behavior_file_has_already_been_analyzed = True
                                print '----------------------------------------------------------------'
                                print 'This behavior file has already been plotted: ' + behavior_file
                                print 'Delete this plot to generate a new version: ' + os.path.join(plot_dirpath, plot_file)            
                    if(behavior_file_has_already_been_analyzed == False):      
                        file_names.append(os.path.join(dirpath, behavior_file))
            
    # sort the file names to analyze them in a 'natural' alphabetical order
    file_names.sort(key=natural_key)    
    print 'Here are all of the behavior files that will be analyzed now:'
    print file_names
    
    # now look for imaging data for each behavior file and combine all the data into one output file    
    for behavior_and_traces in file_names:
        print '----------------------------------------------------------------'
        print '----------------------------------------------------------------'
        print 'Plotting this file: '+ behavior_and_traces

        directory_path_pvalue_files_for_reference_variables = ''
        file_length = len(behavior_and_traces)        
        for name_letter in range (1,file_length):
            if(behavior_and_traces[file_length - name_letter] == '/'):
                directory_path_pvalue_files_for_reference_variables = behavior_and_traces[0:(file_length - name_letter)]
                break

        print 'Checking this location for pvalue files:  ' + directory_path_pvalue_files_for_reference_variables

        pvalue_filenames = [os.path.join(directory_path_pvalue_files_for_reference_variables, f)
            for dirpath, dirnames, files in os.walk(directory_path_pvalue_files_for_reference_variables)
            for f in files if f.endswith('pvalues.csv')]
        pvalue_filenames.sort(key=natural_key)

        #create an output folder for the plots, one folder per mouse 
        # first extract the mouse ID and date from behavior file, to create a folder with the correct name
        mouse_ID_first_letter = 0
        for name_letter in range (1,file_length):
            if(behavior_and_traces[file_length - name_letter] == 'w' or behavior_and_traces[file_length - name_letter] == 'W'):
                mouse_ID_first_letter = file_length - name_letter
                break
        mouse_ID = behavior_and_traces[mouse_ID_first_letter:(mouse_ID_first_letter+7)]
        mouse_ID_and_date = behavior_and_traces[mouse_ID_first_letter:(mouse_ID_first_letter+18)]
        print 'Mouse ID is: %s'%mouse_ID_and_date

        #create create a folder, if it is not already there 
        mouse_plot_output_directory_path = output_directory_path + '/' + mouse_ID  + '/' + mouse_ID_and_date
        if mouse_plot_output_directory_path:
            if not os.path.isdir(mouse_plot_output_directory_path):
                os.makedirs(mouse_plot_output_directory_path)
        
        read_data_and_generate_plots(behavior_and_traces,frames_pre_odor_onset,frames_post_odor_onset,mouse_plot_output_directory_path)

    #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><#


#############################################################################################
#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><#
#############################################################################################

#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def read_data_and_generate_plots(file_path,frames_pre_odor_onset,frames_post_odor_onset,mouse_plot_output_directory_path):
    
    behavior_and_trace_data = numpy.loadtxt(file_path, dtype='float', delimiter=',')
    
    #to plot time as x-axis, transpose the whole array
    behavior_and_trace_data = behavior_and_trace_data.transpose()
    print 'In this recording:'
    print "Events array size is: (%d ,%d)" %(behavior_and_trace_data.shape[0], behavior_and_trace_data.shape[1])
    
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
    #row 12 to last row = trace data for cells in this recording
    
    odor = behavior_and_trace_data[2,:].astype(int) #copy the odor values as integers
    lap_count = behavior_and_trace_data[9,:].astype(int)
    reward_window = behavior_and_trace_data[6,:].astype(int)
    distance = behavior_and_trace_data[7,:].astype(int)
    environment = behavior_and_trace_data[10,:].astype(int)
    running_speed = behavior_and_trace_data[11,:].astype(int) #speed is in mm/s

    #delete the desired number of rows/columns in the desired axis
    trace_data = numpy.delete(behavior_and_trace_data, (0,1,2,3,4,5,6,7,8,9,10,11), axis=0) #here we delete the first 12 rows, which contain the behavior data

    print 'Maximum speed was: %f' %max(running_speed)    
    print 'Minimum speed was: %f' %min(running_speed)

    number_of_environments = max(environment)
    print 'Number of environments = %d' %number_of_environments

    total_number_of_laps = max(lap_count) + 1
    print 'Number of laps = %d' %total_number_of_laps
    
    total_number_of_cells = trace_data.shape[0]
    print 'Number of cells = %d' %total_number_of_cells
    
    total_number_of_frames = trace_data.shape[1]
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
    print 'Number of laps in each enviornment:'
    print laps_in_environment
   
    #find out the odor sequence for each environment
    #this is to print the correct odor sequence on the x-axis
    #and find out the track length in each environment      
    odor_sequence = numpy.zeros((number_of_environments*3),dtype='int')
    odor_start_and_end_points = numpy.zeros((number_of_environments*6),dtype='int')   # 3 odors, 3 start points + 3 end points = 6 total points
    all_laps_odor_start_frames = numpy.zeros((total_number_of_laps*3),dtype='int')   # 3 odors, 3 start frames per lap
    env_track_lengths = numpy.zeros(number_of_environments,dtype='int')
    adjusted_odor_label = numpy.zeros((total_number_of_laps*3),dtype='int') # give unique label to each of the 9 total possible presentations of odor (max of 3 environments with a max of 3 odors each)
  
    ###############################################################################
    for env in range(0,number_of_environments):

        lap_point_where_first_reward_was_presented = 0
        for frame in range(1,total_number_of_frames):
            #if(environment[frame] == env+1 and initial_drops[frame] > initial_drops[frame -1]):      #using the presentation of initial drop to mark the completion of lap      
            if(environment[frame] == env+1 and reward_window[frame] > reward_window[frame -1]):       #using the start of reward window, safer option in cases where initial drop is not presented in some laps
                lap_point_where_first_reward_was_presented = distance[frame]
                break
        env_track_lengths[env] = (lap_point_where_first_reward_was_presented / 100) * 100 #this will round down the distance value to the nearest multiple of 100mm (hopefully giving us 2m, 4m or 8m values)


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
                all_laps_odor_start_frames[lap_count[env_frame]*3 + odor_count_in_this_sequence] = env_frame
                adjusted_odor_label[lap_count[env_frame]*3 + odor_count_in_this_sequence] = env*3 + odor_count_in_this_sequence + 1
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
 
    print 'Odor sequence in each environment (3 odors per environment):'
    print odor_sequence
    print 'Odors sequence in letters (3 odors per environment):'
    print odor_sequence_in_letters
    print 'The odors start and end at these distance points:'
    print odor_start_and_end_points           
    print 'The track lengths in all enviornments are:'
    print env_track_lengths

    print 'The odors start and end at these frames in each lap:'
    print all_laps_odor_start_frames 
    print 'Adjusted odor labels:'
    print adjusted_odor_label 


    ###############################################################################
    ############generate ranking for cells according to max response###############
    ###############################################################################

#    trace_matrices = [list(numpy.zeros((total_number_of_cells,laps_in_environment[],dtype='float')) for ref_var in xrange(number_of_reference_variables)] 

    adjusted_odors,laps_with_this_adjusted_odor = get_unique_elements(adjusted_odor_label,return_index=False, return_inverse=False,return_counts=True)
    adjusted_odors = adjusted_odors[1:]
    laps_with_this_adjusted_odor = laps_with_this_adjusted_odor[1:]
    print 'All adjusted odors and the number of laps with those odors:'
    print adjusted_odors
    print laps_with_this_adjusted_odor

    number_of_frames_in_trace_plot = frames_pre_odor_onset + frames_post_odor_onset
    for cell in xrange(2):
        trace_matrices = [list(numpy.zeros((laps_with_this_adjusted_odor[odor],number_of_frames_in_trace_plot),dtype='float')) for odor in xrange(len(adjusted_odors))]
        
        trace_data_for_this_cell = trace_data[cell,:]
        
        for odor in xrange(len(trace_matrices)):
            odor_lap_count = 0
            for unknown_odor in xrange(len(all_laps_odor_start_frames)):
                if(adjusted_odor_label[unknown_odor] == adjusted_odors[odor]):
                    #print trace_data_for_this_cell[all_laps_odor_start_frames[unknown_odor]-frames_pre_odor_onset:all_laps_odor_start_frames[unknown_odor]+frames_post_odor_onset]
                    if(all_laps_odor_start_frames[unknown_odor]-frames_pre_odor_onset > 0 and all_laps_odor_start_frames[unknown_odor]+frames_post_odor_onset < total_number_of_frames):
                        trace_matrices[odor][odor_lap_count][:] = trace_data_for_this_cell[all_laps_odor_start_frames[unknown_odor]-frames_pre_odor_onset:all_laps_odor_start_frames[unknown_odor]+frames_post_odor_onset]
                        odor_lap_count += 1
                    elif(all_laps_odor_start_frames[unknown_odor]-frames_pre_odor_onset < 0 and all_laps_odor_start_frames[unknown_odor]+frames_post_odor_onset < total_number_of_frames):
                        print 'starting from the zeroth frame for odor %d'%adjusted_odors[odor]
                        empty_part_of_this_list_at_the_beginning = [0.00]*(frames_pre_odor_onset - all_laps_odor_start_frames[unknown_odor])
                        trace_matrices[odor][odor_lap_count][:] =  numpy.append(empty_part_of_this_list_at_the_beginning,trace_data_for_this_cell[0:all_laps_odor_start_frames[unknown_odor]+frames_post_odor_onset])
                        print len(numpy.append(empty_part_of_this_list_at_the_beginning,trace_data_for_this_cell[0:all_laps_odor_start_frames[unknown_odor]+frames_post_odor_onset]))
                        odor_lap_count += 1                        
                    elif(all_laps_odor_start_frames[unknown_odor]-frames_pre_odor_onset > 0 and all_laps_odor_start_frames[unknown_odor]+frames_post_odor_onset > total_number_of_frames):
                        print 'beyond max frame for odor %d'%adjusted_odors[odor]
                        empty_part_of_this_list_at_the_end = [0.00]*(all_laps_odor_start_frames[unknown_odor]+frames_post_odor_onset - total_number_of_frames)
                        trace_matrices[odor][odor_lap_count][:] = numpy.append(trace_data_for_this_cell[all_laps_odor_start_frames[unknown_odor]-frames_pre_odor_onset:total_number_of_frames],empty_part_of_this_list_at_the_end)
                        print len(numpy.append(trace_data_for_this_cell[all_laps_odor_start_frames[unknown_odor]-frames_pre_odor_onset:total_number_of_frames],empty_part_of_this_list_at_the_end))
                        odor_lap_count += 1


            
            graph_this_cell(trace_matrices,adjusted_odors)

            numpy.savetxt(file_path.replace('.csv','_traces_for_cell%d.csv'%cell), trace_matrices[1], fmt='%1.5f', delimiter=',', newline='\n')                    
                    
#            for lap in xrange(laps_with_this_adjusted_odor[odor]):
#                if(all_laps_odor_start_frames)
#                trace_matrices[odor][lap][:] = 
#            
#                for frame in xrange()


    #    np.savetxt(file_path.replace('.csv','_total_events_per_bin.csv'), total_events_per_bin_per_cell, fmt='%i', delimiter=',', newline='\n') 
           
    
        #now send the data for plotting:
#        generate_plots(file_path,place_data_each_cell,number_of_environments,laps_in_environment,total_number_of_cells,env_track_lengths,odor_sequence_in_letters,odor_start_and_end_points,mouse_plot_output_directory_path)

    ###############################################################################
    ########################done generating data for plots ########################
    ###############################################################################


###############################################################################
###############################################################################
###################### now we plot some good nice heatmaps ####################
###############################################################################
###############################################################################
#based on source: http://stackoverflow.com/questions/14391959/heatmap-in-matplotlib-with-pcolor
def generate_plots(file_path, place_data_each_cell,number_of_environments, laps_in_environment, total_number_of_cells,env_track_lengths,odor_sequence_in_letters,odor_start_and_end_points,mouse_plot_output_directory_path):

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
            data_array = numpy.zeros((1,data_array_all.shape[1]))
        elif(len(data_array) == data_array_all.shape[1]):
            data_array = numpy.vstack([numpy.zeros((1,data_array_all.shape[1])),data_array])            
        
        number_of_cells_in_this_plot = data_array.shape[0] 
        
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
            plt.figtext(0.84,0.1,"Cells in env: %d" %number_of_cells_in_this_plot,         fontsize='x-small', color=plot_color[plot_env], ha ='left')
            
            plt.figtext(0.03,0.15,"%d" %number_of_cells_in_this_plot,                      fontsize='large', color = plot_color[plot_env], ha ='left')
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

#            x1 = float(env_track_lengths[env])
#            x2 = x1 / (8 * 1000) # there are eight points on the x-axis, other than the 0
#            x3 = [x2*0, x2*1 , x2*2 , x2*3 , x2*4 , x2*5 , x2*6 , x2*7 , x2*8 ]
#            x3 = numpy.around(x3, decimals=2)
#            ax.set_xlabel('Distance(m)')
##            ax.xaxis.set_major_locator(ticker.MaxNLocator(8))
##            plt.setp(ax,xticklabels=x3,visible=True)
#            xaxis_start, xaxis_end = ax.get_xlim()
#            ax.xaxis.set_ticks(numpy.arange(xaxis_start, xaxis_end*9/8, xaxis_end/8))
#            plt.setp(ax,xticklabels=x3,visible=True)

            x1 = env_track_lengths[env] / 500 # lets say, we want a distance label on the x-axis for every 0.5m (500mm)
            x2 = [0,0.5] # there will be at least two labels on the x-axis, lets see if there will be more
            for x_label in range(2,x1+1):
                x2.append(x_label*0.5)

            ax.xaxis.tick_bottom()   
            ax.set_xlabel('Distance(m)')
            xaxis_start, xaxis_end = ax.get_xlim()
            ax.xaxis.set_ticks(numpy.arange(xaxis_start, xaxis_end+(500/distance_bin_size), (500/distance_bin_size)))
            plt.setp(ax,xticklabels=x2,visible=True)

            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            if(number_of_cells_in_this_plot >= 10):
                ax.yaxis.set_major_locator(ticker.MaxNLocator(number_of_cells_in_this_plot/5))
            ax.set_ylabel('Cell#')
      
            plt.xlim (0,bins_in_environment[env])
            plt.ylim (0,number_of_cells_in_this_plot) 
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


            fig.add_subplot(ax)
     
            #can be commented out to stop showing all plots in the console
            plt.show()
            figs.append(fig)
#            if (env == plot_env):
#                env_aligned_to_itself_figs.append(fig)                
            plt.close()



###############################################################################
#### done generating plots for normalized average speed in each environment ###
###############################################################################
    
    if len(figs) > 0: 
        pdf_file_location = ''
        file_length = len(pvalue_filename)        
        for name_letter in range (1,file_length):
            if(pvalue_filename[file_length - name_letter] == '/'):
                pdf_file_location = mouse_plot_output_directory_path + '/' + pvalue_filename[(file_length - name_letter):(file_length-4)]
                break 

        pdf_name = pdf_file_location + '_place_cells_%1.2f.pdf'%lower_threshold_for_activity
           
        if(split_laps_in_environment == 5050):            
            pdf_name = pdf_file_location + '_place_cells_earlier_vs_later_%1.2f.pdf'%lower_threshold_for_activity 
        elif(split_laps_in_environment == 1212):            
            pdf_name = pdf_file_location + '_place_cells_odd_vs_even_%1.2f.pdf'%lower_threshold_for_activity    
                   
        pp = PdfPages(pdf_name)
        for fig in figs:
                pp.savefig(fig,dpi=300,edgecolor='r')
        pp.close()



###############################################################################
###############################################################################


##this function was copied from the numpy source file as is##
##the source is here: https://github.com/numpy/numpy/blob/v1.9.1/numpy/lib/arraysetops.py#L96
def get_unique_elements(ar, return_index=False, return_inverse=False, return_counts=False):

    ar = numpy.asanyarray(ar).flatten()

    optional_indices = return_index or return_inverse
    optional_returns = optional_indices or return_counts

    if ar.size == 0:
        if not optional_returns:
            ret = ar
        else:
            ret = (ar,)
            if return_index:
                ret += (numpy.empty(0, numpy.bool),)
            if return_inverse:
                ret += (numpy.empty(0, numpy.bool),)
            if return_counts:
                ret += (numpy.empty(0, numpy.intp),)
        return ret

    if optional_indices:
        perm = ar.argsort(kind='mergesort' if return_index else 'quicksort')
        aux = ar[perm]
    else:
        ar.sort()
        aux = ar
    flag = numpy.concatenate(([True], aux[1:] != aux[:-1]))

    if not optional_returns:
        ret = aux[flag]
    else:
        ret = (aux[flag],)
        if return_index:
            ret += (perm[flag],)
        if return_inverse:
            iflag = numpy.cumsum(flag) - 1
            iperm = perm.argsort()
            ret += (numpy.take(iflag, iperm),)
        if return_counts:
            idx = numpy.concatenate(numpy.nonzero(flag) + ([ar.size],))
            ret += (numpy.diff(idx),)
    return ret


###############################################################################
###############################################################################

main()