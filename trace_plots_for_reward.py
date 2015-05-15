import matplotlib.pyplot as plt # needed for plotting graphs
import numpy # needed for various math tasks
from matplotlib.backends.backend_pdf import PdfPages # for saving figures as pdf
import os # needed to find files
import re # needed to arrange filenames alphabetically
import matplotlib.cm as mplcm
import matplotlib.colors as colors
from matplotlib.collections import Collection
from matplotlib.artist import allow_rasterization
import gc

def main():
    # specify the various parameters as needed:
    frames_pre_reward_onset = 50 #time in milliseconds
    frames_post_reward_onset = 50 #time in milliseconds

    data_files_directory_path ='/Users/njoshi/Desktop/data_analysis/input_files'
    output_directory_path = '/Users/njoshi/Desktop/data_analysis/output_files'

#    data_files_directory_path  = '/Volumes/walter/Virtual_Odor/imaging_data/wfnjC08'
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
                    for i in xrange(len(behavior_file)):
                        if(behavior_file[i] == '_'):
                            mouse_ID = behavior_file[0:i]
                            mouse_ID_and_date = behavior_file[0:i+11]
                            break
                    for plot_dirpath, plot_dirnames, plot_files in os.walk(output_directory_path + '/' + mouse_ID + '/reward_trace_plots'):                    
                        for plot_file in plot_files:
                            if plot_file.endswith(mouse_ID_and_date + '_reward_trace_plots.pdf'):  
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
    for behavior_and_traces_file_path in file_names:
        print '----------------------------------------------------------------'
        print '----------------------------------------------------------------'
        print 'Plotting this file: '+ behavior_and_traces_file_path
        
        read_data_and_generate_plots(behavior_and_traces_file_path,frames_pre_reward_onset,frames_post_reward_onset,output_directory_path)

    #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><#


#############################################################################################
#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><#
#############################################################################################

#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def read_data_and_generate_plots(behavior_and_traces_file_path,frames_pre_reward_onset,frames_post_reward_onset,output_directory_path):
    
    behavior_and_trace_data = numpy.loadtxt(behavior_and_traces_file_path, dtype='float', delimiter=',')
    
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
    odor_sequence = numpy.zeros((number_of_environments*4),dtype='int')
    odor_start_and_end_points = numpy.zeros((number_of_environments*8),dtype='int')   # 3 odors, 3 start points + 3 end points = 6 total points
    all_laps_odor_start_frames = numpy.zeros((total_number_of_laps*4),dtype='int')   # 3 odors, 3 start frames per lap
    all_laps_reward_start_frames = numpy.zeros((total_number_of_laps),dtype='int')   # 1 reward window per lap
    env_track_lengths = numpy.zeros(number_of_environments,dtype='int')
    adjusted_odor_label = numpy.zeros((total_number_of_laps*4),dtype='int') # give unique label to each of the 9 total possible presentations of odor (max of 3 environments with a max of 3 odors each)
  
    ###############################################################################

    last_lap_evaluated =  -1
    for frame in range(1,total_number_of_frames):    
        if(reward_window[frame] > reward_window[frame -1] and lap_count[frame] > last_lap_evaluated):       #using the start of reward window, safer option in cases where initial drop is not presented in some laps
            all_laps_reward_start_frames[lap_count[frame]] = frame
            last_lap_evaluated = lap_count[frame]

#    print 'Reward start frames:'
#    print all_laps_reward_start_frames

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
        for env_frame in range(2,total_number_of_frames):
            if(environment[env_frame] == env+1 and odor[env_frame] > odor[env_frame-1]  and odor[env_frame] > odor[env_frame-2]):
                lap_under_evaluation = lap_count[env_frame]
                odor_sequence[env*4 + odor_count_in_this_sequence] = odor[env_frame]
                sum_of_odor_start_points = distance[env_frame] + odor_start_and_end_points[env*8 + odor_count_in_this_sequence*2]
                odor_start_and_end_points[env*8 + odor_count_in_this_sequence*2] = sum_of_odor_start_points #this is where the odor starts, distance has been rounded to nearest 50mm
                all_laps_odor_start_frames[lap_count[env_frame]*4 + odor_count_in_this_sequence] = env_frame
                adjusted_odor_label[lap_count[env_frame]*4 + odor_count_in_this_sequence] = env*4 + odor_count_in_this_sequence + 1
            elif(environment[env_frame] == env+1 and odor[env_frame] < odor[env_frame-1] and odor[env_frame] < odor[env_frame-2]):
                sum_of_odor_end_points = distance[env_frame] + odor_start_and_end_points[env*8 + odor_count_in_this_sequence*2 + 1]
                odor_start_and_end_points[env*8 + odor_count_in_this_sequence*2 + 1] = sum_of_odor_end_points
                odor_count_in_this_sequence = odor_count_in_this_sequence + 1
            elif(lap_count[env_frame] > lap_under_evaluation or odor_count_in_this_sequence >= 4):
                odor_count_in_this_sequence = 0

        for odor_point in range(0,8):
            average_distance_odor_point = odor_start_and_end_points[env*8 + odor_point] / laps_in_environment[env]
            odor_start_and_end_points[env*8 + odor_point] = average_distance_odor_point

    ###############################################################################

    odor_labels = [' ','A','B','C','D','E','F','G']
    odor_sequence_in_letters = ['']*len(odor_sequence)
    
    #change odor labels from numbers to letters
    for odor in xrange (len(odor_sequence)):
        odor_sequence_in_letters[odor] = odor_labels[odor_sequence[odor]]
           
 
    print 'Odor sequence in each environment (4 odors per environment):'
    print odor_sequence
    print 'Odors sequence in letters (4 odors per environment):'
    print odor_sequence_in_letters
    print 'The odors start and end at these distance points:'
    print odor_start_and_end_points           
    print 'The track lengths in all enviornments are:'
    print env_track_lengths

#    print 'The odors start and end at these frames in each lap:'
#    print all_laps_odor_start_frames 
#    print 'Adjusted odor labels:'
#    print adjusted_odor_label 

#    trace_matrices = [list(numpy.zeros((total_number_of_cells,laps_in_environment[],dtype='float')) for ref_var in xrange(number_of_reference_variables)] 

    number_of_frames_in_trace_plot = frames_pre_reward_onset + frames_post_reward_onset
    adjusted_odors,laps_with_this_adjusted_odor = get_unique_elements(adjusted_odor_label,return_index=False, return_inverse=False,return_counts=True)
    adjusted_odors = adjusted_odors[1:]
    laps_with_this_adjusted_odor = laps_with_this_adjusted_odor[1:]
    print 'All adjusted odors and the number of laps with those odors:'
    print adjusted_odors
    print laps_with_this_adjusted_odor

    #plot the reward trace only once per environment    
    reduced_adjusted_odor = []
    reduced_laps_with_this_adjusted_odor = []
    last_env = -1
    for this_odor in xrange(len(adjusted_odors)):
        if((adjusted_odors[this_odor]-1)/4 > last_env):
            last_env = (adjusted_odors[this_odor]-1)/4
            reduced_adjusted_odor.append(adjusted_odors[this_odor])
            reduced_laps_with_this_adjusted_odor.append(laps_with_this_adjusted_odor[this_odor])     

    adjusted_odors = reduced_adjusted_odor
    laps_with_this_adjusted_odor = reduced_laps_with_this_adjusted_odor
    print 'One adjusted odor per environment and the number of laps with those odors:'
    print adjusted_odors
    print laps_with_this_adjusted_odor            



    #for printing trial information on the plots
    sequence_of_environments = ''
    sequence_of_lap_counts   = ''
    sequence_of_track_lengths= ''
    for env in range(0,number_of_environments):
        sequence_of_environments = sequence_of_environments + odor_sequence_in_letters[4*env] + odor_sequence_in_letters[4*env+1] + odor_sequence_in_letters[4*env+2] + odor_sequence_in_letters[4*env+3]
        sequence_of_lap_counts = sequence_of_lap_counts + str(laps_in_environment[env])
        sequence_of_track_lengths = sequence_of_track_lengths + str( float(env_track_lengths[env]) / 1000.00)
        if(env < number_of_environments-1):
            sequence_of_environments = sequence_of_environments + ','
            sequence_of_lap_counts = sequence_of_lap_counts + ','
            sequence_of_track_lengths = sequence_of_track_lengths + ','
    print 'This is the sequence of environments: %s' %sequence_of_environments

    ###############################################################################
    ############generate file location and filename for output pdf  ###############
    ###############################################################################

    #only try to generate plots if there was at least one odor in this recording
    if(len(adjusted_odors) > 0):
        #first specify the location for this output pdf:
        behavior_and_traces_file_location,behavior_and_traces_filename = os.path.split(behavior_and_traces_file_path)
    
        #create an output folder for the plots, one folder per mouse 
        # first extract the mouse ID and date from behavior file, to create a folder with the correct name
        for i in xrange(len(behavior_and_traces_filename)):
            if(behavior_and_traces_filename[i] == '_'):
                mouse_ID = behavior_and_traces_filename[0:i]
                mouse_ID_and_date = behavior_and_traces_filename[0:i+11]
                break
        print 'Mouse ID is: %s'%mouse_ID_and_date
    
        #create an output folder, if it is not already there 
        pdf_output_directory_path = output_directory_path + '/' + mouse_ID  + '/reward_trace_plots'
        if pdf_output_directory_path:
            if not os.path.isdir(pdf_output_directory_path):
                os.makedirs(pdf_output_directory_path)
    
        pdf_filename = pdf_output_directory_path + '/' + mouse_ID_and_date + '_reward_trace_plots.pdf'
        pp = PdfPages(pdf_filename) 
    
        ###############################################################################
        ##########done generating file location and filename for output pdf  ##########
        ###############################################################################



        #now for each cell, generate matrices of traces for each odor to be plotted, then plot these matrices in a single figure
        #total_number_of_cells
        for cell in xrange(2):
            print 'Plotting cell# %  d of %d'%(cell,total_number_of_cells)  
            trace_matrices = [list(numpy.zeros((laps_with_this_adjusted_odor[odor],number_of_frames_in_trace_plot),dtype='float')) for odor in xrange(len(adjusted_odors))]
    
            trace_data_for_this_cell = trace_data[cell,:]
            for odor in xrange(len(trace_matrices)):
                odor_lap_count = 0
                for unknown_odor in xrange(len(adjusted_odor_label)):
                    if(adjusted_odor_label[unknown_odor] == adjusted_odors[odor]):
                        current_lap = unknown_odor / 4
                        #print 'reward plot'
                        #select the trace data from the right range of frames in each lap
                        if(all_laps_reward_start_frames[current_lap]-frames_pre_reward_onset > 0 and all_laps_reward_start_frames[current_lap]+frames_post_reward_onset < total_number_of_frames):                           
                            trace_matrices[odor][odor_lap_count][:] = trace_data_for_this_cell[all_laps_reward_start_frames[current_lap]-frames_pre_reward_onset:all_laps_reward_start_frames[current_lap]+frames_post_reward_onset]
                            odor_lap_count += 1
                        elif(all_laps_reward_start_frames[current_lap]-frames_pre_reward_onset < 0 and all_laps_reward_start_frames[current_lap]+frames_post_reward_onset < total_number_of_frames):
                            empty_part_of_this_list_at_the_beginning = [0.00]*(frames_pre_reward_onset - all_laps_reward_start_frames[current_lap])
                            trace_matrices[odor][odor_lap_count][:] =  numpy.append(empty_part_of_this_list_at_the_beginning,trace_data_for_this_cell[0:all_laps_reward_start_frames[current_lap]+frames_post_reward_onset])
                            odor_lap_count += 1                        
                        elif(all_laps_reward_start_frames[current_lap]-frames_pre_reward_onset > 0 and all_laps_reward_start_frames[current_lap]+frames_post_reward_onset > total_number_of_frames):
                            empty_part_of_this_list_at_the_end = [0.00]*(all_laps_reward_start_frames[current_lap]+frames_post_reward_onset - total_number_of_frames)
                            trace_matrices[odor][odor_lap_count][:] = numpy.append(trace_data_for_this_cell[all_laps_reward_start_frames[current_lap]-frames_pre_reward_onset:total_number_of_frames],empty_part_of_this_list_at_the_end)
                            odor_lap_count += 1
            graph_this_cell(pp,mouse_ID_and_date,cell,trace_matrices,adjusted_odors,odor_sequence_in_letters,number_of_frames_in_trace_plot,frames_pre_reward_onset,sequence_of_environments,sequence_of_lap_counts,sequence_of_track_lengths,total_number_of_cells)          
        pp.close()
        gc.collect()
        print 'Done saving pdf'
    else:
        print 'There were no odors in this recording.'
         
    ###############################################################################
    ########################done generating data for plots ########################
    ###############################################################################


#def graph_this_cell(fig,axs,mouse_ID_and_date,cell_index,trace_matrices,adjusted_odors,odor_sequence_in_letters,number_of_frames_in_trace_plot,frames_pre_reward_onset,sequence_of_environments,sequence_of_lap_counts,sequence_of_track_lengths,total_number_of_cells):

def graph_this_cell(pp,mouse_ID_and_date,cell_index,trace_matrices,adjusted_odors,odor_sequence_in_letters,number_of_frames_in_trace_plot,frames_pre_reward_onset,sequence_of_environments,sequence_of_lap_counts,sequence_of_track_lengths,total_number_of_cells):
  
    number_of_subplots = len(adjusted_odors)            

    fig,axs = plt.subplots(number_of_subplots, sharex=True, sharey=True)   
    fig.subplots_adjust(hspace=0.15)
    fig.suptitle('%s   Reward trace plots for cell#%d / %d' %(mouse_ID_and_date,cell_index,total_number_of_cells))
    plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
    plt.figtext(0.01,0.98,"envs   :%s" %sequence_of_environments,fontsize='xx-small', color='red', ha ='left')
    plt.figtext(0.01,0.96,"laps    :%s"%sequence_of_lap_counts ,fontsize='xx-small', color='red', ha ='left')
    plt.figtext(0.01,0.94,"len(m):%s"  %sequence_of_track_lengths,fontsize='xx-small', color='red', ha ='left')

    plt.figtext((frames_pre_reward_onset*1.00/number_of_frames_in_trace_plot),0.905,"Reward",fontsize='xx-small', color='blue', ha ='left')
    
    for ax in xrange(len(axs)):

        #this is to change the color of trace line in each lap, from blue to red
        NUM_COLORS = len(trace_matrices[ax])
        cm = plt.get_cmap('jet')
        cNorm  = colors.Normalize(vmin=0, vmax=NUM_COLORS-1)
        scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)
        axs[ax].set_color_cycle([scalarMap.to_rgba(i) for i in range(NUM_COLORS)])

        for lap in xrange(len(trace_matrices[ax])): 
            axs[ax].plot(range(number_of_frames_in_trace_plot),trace_matrices[ax][lap],linewidth = 0.2)

        #to mark the frame for odor onset with a blue verticle line
        axs[ax].axvline(x=frames_pre_reward_onset, linewidth=0.2, color='b')
        
        this_env = (adjusted_odors[ax]-1)/4
        this_odor = odor_sequence_in_letters[adjusted_odors[ax]-1]
        this_odor_index = (adjusted_odors[ax]-1)%4+1
        axs[ax].set_ylabel('env%d'%(this_env+1),rotation='horizontal',horizontalalignment='right',color='red',fontsize='x-small')
        
        axs[ax].tick_params(axis='y', which='major', labelsize=4) #for small yaxis labels

        [i.set_linewidth(0.1) for i in axs[ax].spines.itervalues()] #for thin border lines
        axs[ax].set_xlim(0,number_of_frames_in_trace_plot)

        #for efficiently rasterizing the plot
        insert(axs[ax])

#    plt.show()
    pp.savefig()
    plt.close(fig)

###############################################################################
######## insert(c) efficiently rasterize the plots into small size ############
#### Source: http://sourceforge.net/p/matplotlib/mailman/message/27941302/ ####
###############################################################################

class ListCollection(Collection):
     def __init__(self, collections, **kwargs):
         Collection.__init__(self, **kwargs)
         self.set_collections(collections)
     def set_collections(self, collections):
         self._collections = collections
     def get_collections(self):
         return self._collections
     @allow_rasterization
     def draw(self, renderer):
         for _c in self._collections:
             _c.draw(renderer)

def insert(c):
     collections = c.collections
     for _c in collections:
         _c.remove()
     cc = ListCollection(collections, rasterized=True)
     ax = plt.gca()
     ax.add_artist(cc)
     return cc


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