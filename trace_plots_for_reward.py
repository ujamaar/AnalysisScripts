import matplotlib.pyplot as plt # needed for plotting graphs
import numpy # needed for various math tasks
from matplotlib.backends.backend_pdf import PdfPages # for saving figures as pdf
import os # needed to find files
import re # needed to arrange filenames alphabetically
import matplotlib.cm as mplcm
import matplotlib.colors as colors
from matplotlib.collections import Collection
from matplotlib.artist import allow_rasterization

def main():
    # specify the various parameters as needed:
    frames_pre_odor_onset = 50 #time in milliseconds
    frames_post_odor_onset = 100 #time in milliseconds

    data_files_directory_path ='/Users/njoshi/Desktop/data_analysis/input_files'
    output_directory_path = '/Users/njoshi/Desktop/data_analysis/output_files'

#    data_files_directory_path  = '/Volumes/walter/Virtual_Odor/imaging_data/'
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
    for behavior_and_traces_file_path in file_names:
        print '----------------------------------------------------------------'
        print '----------------------------------------------------------------'
        print 'Plotting this file: '+ behavior_and_traces_file_path
        
        read_data_and_generate_plots(behavior_and_traces_file_path,frames_pre_odor_onset,frames_post_odor_onset,output_directory_path)

    #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><#


#############################################################################################
#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><#
#############################################################################################

#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def read_data_and_generate_plots(behavior_and_traces_file_path,frames_pre_odor_onset,frames_post_odor_onset,output_directory_path):
    
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

    odor_labels = [' ','A','B','C','D','E','F','G']
    odor_sequence_in_letters = ['']*len(odor_sequence)
    
    #change odor labels from numbers to letters
    for odor in xrange (len(odor_sequence)):
        odor_sequence_in_letters[odor] = odor_labels[odor_sequence[odor]]
           
 
    print 'Odor sequence in each environment (3 odors per environment):'
    print odor_sequence
    print 'Odors sequence in letters (3 odors per environment):'
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

    adjusted_odors,laps_with_this_adjusted_odor = get_unique_elements(adjusted_odor_label,return_index=False, return_inverse=False,return_counts=True)
    adjusted_odors = adjusted_odors[1:]
    laps_with_this_adjusted_odor = laps_with_this_adjusted_odor[1:]
    print 'All adjusted odors and the number of laps with those odors:'
    print adjusted_odors
    print laps_with_this_adjusted_odor
    number_of_frames_in_trace_plot = frames_pre_odor_onset + frames_post_odor_onset

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
        pdf_output_directory_path = output_directory_path + '/' + mouse_ID  + '/' + 'trace_plots'
        if pdf_output_directory_path:
            if not os.path.isdir(pdf_output_directory_path):
                os.makedirs(pdf_output_directory_path)
    
        pdf_filename = pdf_output_directory_path + '/' + mouse_ID_and_date + '_trace_plots_%d_frames.pdf'%number_of_frames_in_trace_plot
        pp = PdfPages(pdf_filename) 
    
        ###############################################################################
        ##########done generating file location and filename for output pdf  ##########
        ###############################################################################
    
    
#        figs = []
        #now for each cell, generate matrices of traces for each odor to be plotted, then plot these matrices in a single figure
        #total_number_of_cells
        for cell in xrange(total_number_of_cells):
            print 'Plotting cell# %  d of %d'%(cell,total_number_of_cells)  
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
                            empty_part_of_this_list_at_the_beginning = [0.00]*(frames_pre_odor_onset - all_laps_odor_start_frames[unknown_odor])
                            trace_matrices[odor][odor_lap_count][:] =  numpy.append(empty_part_of_this_list_at_the_beginning,trace_data_for_this_cell[0:all_laps_odor_start_frames[unknown_odor]+frames_post_odor_onset])
                            odor_lap_count += 1                        
                        elif(all_laps_odor_start_frames[unknown_odor]-frames_pre_odor_onset > 0 and all_laps_odor_start_frames[unknown_odor]+frames_post_odor_onset > total_number_of_frames):
                            empty_part_of_this_list_at_the_end = [0.00]*(all_laps_odor_start_frames[unknown_odor]+frames_post_odor_onset - total_number_of_frames)
                            trace_matrices[odor][odor_lap_count][:] = numpy.append(trace_data_for_this_cell[all_laps_odor_start_frames[unknown_odor]-frames_pre_odor_onset:total_number_of_frames],empty_part_of_this_list_at_the_end)
                            odor_lap_count += 1
              
            cell_figure = graph_this_cell(mouse_ID_and_date,cell,trace_matrices,adjusted_odors,odor_sequence_in_letters,number_of_frames_in_trace_plot,frames_pre_odor_onset)          
            pp.savefig(cell_figure)
#            figs.append(cell_figure)    
    #        numpy.savetxt(file_path.replace('.csv','_traces_for_cell%d.csv'%cell), trace_matrices[1], fmt='%1.5f', delimiter=',', newline='\n') 
                    
                       
        #now save all figures in a pdf, one figure for each cell
#        for fig in figs:
#                pp.savefig(fig)
        pp.close()
        print 'Done saving pdf'

    else:
        print 'There were no odors in this recording.'
         
    ###############################################################################
    ########################done generating data for plots ########################
    ###############################################################################



def graph_this_cell(mouse_ID_and_date,cell_index,trace_matrices,adjusted_odors,odor_sequence_in_letters,number_of_frames_in_trace_plot,frames_pre_odor_onset):
  
    number_of_subplots = len(adjusted_odors)            

    fig,axs = plt.subplots(number_of_subplots, sharex=True, sharey=True)   
    fig.subplots_adjust(hspace=0.15)
#    fig.set_rasterized(True)
    fig.suptitle('%s   Cell#%d odor trace plots for all trials' %(mouse_ID_and_date,cell_index))

    
    for ax in xrange(len(axs)):

        #this is to change the color of trace line in each lap, from blue to red
        NUM_COLORS = len(trace_matrices[ax])
        cm = plt.get_cmap('jet')
        cNorm  = colors.Normalize(vmin=0, vmax=NUM_COLORS-1)
        scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)
        axs[ax].set_color_cycle([scalarMap.to_rgba(i) for i in range(NUM_COLORS)])

        for lap in xrange(len(trace_matrices[ax])): 
            axs[ax].plot(range(number_of_frames_in_trace_plot),trace_matrices[ax][lap],linewidth = 0.2)

        #to mark the frame for odor onset, with a blue verticle line
        axs[ax].axvline(x=frames_pre_odor_onset, linewidth=0.2, color='b')
        
        this_env = (adjusted_odors[ax]-1)/3
        this_odor = odor_sequence_in_letters[adjusted_odors[ax]-1]
        this_odor_index = (adjusted_odors[ax]-1)%3+1
        axs[ax].set_ylabel('Env%d \n %s%d'%(this_env,this_odor,this_odor_index),rotation='horizontal',horizontalalignment='right',color='red')
        
        axs[ax].tick_params(axis='y', which='major', labelsize=4) #for small yaxis labels

        [i.set_linewidth(0.1) for i in axs[ax].spines.itervalues()] #for thin border lines
        axs[ax].set_xlim(0,number_of_frames_in_trace_plot)

        #for efficiently rasterizing the plot
        insert(axs[ax])

    plt.setp([a.get_xticklabels() for a in fig.axes[:-1]], visible=False)
    return_figure = fig
    plt.close(fig)

    
    return return_figure

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