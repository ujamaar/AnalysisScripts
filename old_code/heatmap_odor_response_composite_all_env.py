#based on source: http://stackoverflow.com/questions/14391959/heatmap-in-matplotlib-with-pcolor
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import os

#for PC, the format is something like: directory_path ='C:/Users/axel/Desktop/test_data'
directory_path ='/Users/njoshi/Desktop/events_test'

file_names = [os.path.join(directory_path, f)
    for dirpath, dirnames, files in os.walk(directory_path)
    for f in files if f.endswith('.csv')]

file_path = ''
if(len(file_names) == 1):
    file_path = file_names[0]
    print 'Analyzing this file:'
    print file_names[0]
else:
    print 'Make sure that there is only one .csv file in the selected folder'

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

odor = event_data[2,:]
lap_count = event_data[6,:]
total_laps = max(lap_count) + 1

distance = event_data[5,:]
track_length = max(distance)

expansion_factor = 0
while(True):
    if((track_length > expansion_factor*4500) and (track_length <= (expansion_factor+1)*4500)):
        track_length = (expansion_factor+1)*4500
        expansion_factor = expansion_factor+1
        break
    else:
        expansion_factor = expansion_factor+1  
print 'Track length = %dmm'%track_length

environment = event_data[7,:]
number_of_environments = max(environment)
print 'Number of laps = %d' %total_laps
print 'Number of environments = %d' %number_of_environments
#print odor[0:15]


#delete the desired number of rows/columns in the desired axis
event_data = np.delete(event_data, (0,1,2,3,4,5,6,7,8), axis=0)
total_number_of_cells = event_data.shape[0]
print 'Number of cells = %d' %total_number_of_cells
total_number_of_frames = event_data.shape[1]
print 'Number of imaging frames: %d'%total_number_of_frames

#print a portion of the event data just to check
#print event_data[0:10,0:10]

###############################################################################
###### add the events in response to each odor in each lap
###############################################################################

number_of_odors = 4
odor_start_points = [250*expansion_factor,1250*expansion_factor,2250*expansion_factor,3250*expansion_factor]
print 'A new odor is turned on at each of these points in a lap of %dmm:'%track_length
print odor_start_points


event_data_for_plotting = np.empty((total_number_of_cells,total_number_of_frames),dtype='int') 

for row in range(0,total_number_of_cells):
    current_lap = 0
    current_odor = -1

    if (row % 20 == 0):
        print 'Processing cell# %d / %d'%(row,total_number_of_cells)

    #run thi while loop until all columns have been checked for the cell in this row
    column = 1    
    while (column < total_number_of_frames):
        #if statement is true at the start of each new lap
        if(lap_count[column] == lap_count[column-1]):
            current_lap = lap_count[column]
            #print 'we are in lap %d'%current_lap
            #this while loop is true as long as the current lap lasts
            while((column < total_number_of_frames) and (lap_count[column] == lap_count[column-1])):    #for each lap
                #this if-statement is true only for non-zero odors
                if((odor[column]>0) and (odor[column] == odor[column-1])):
                    current_odor = current_odor + 1
                    odor_response = 0
                    #this while loop is true as long as the current odor is ON
                    while((column < total_number_of_frames) and (odor[column]==odor[column-1])):         #for each odor in each lap
                        odor_response = odor_response + event_data[row][column]
                        column = column + 1
                    event_data_for_plotting[row][current_lap*number_of_odors + current_odor] = odor_response
                else:
                    column = column + 1
        else:
            column = column + 1
                    
                

###############################################################################
###### calculate the proportion of laps for each odor that had an event #######
              # also account for different environments #
###############################################################################

environment_transitions = [0]

for column in range(1,total_number_of_frames):
    if(environment[column] > environment[column-1]):
        environment_transitions.append(lap_count[column])

environment_transitions.append(lap_count[total_number_of_frames-1])
print 'A new environment starts in these laps:'
print environment_transitions


#this is to print the correct odor sequence on the x-axis
odor_sequence = np.zeros((number_of_environments*number_of_odors),dtype='int')

for env in range(0,number_of_environments):
    current_odor_position = 0
    for column in range(1,len(odor)):
        if(lap_count[column] == environment_transitions[env]): #look at first lap of the new environment
            if(odor[column] > odor[column-1]):                 #find when an odor turns on
                if(int(odor[column]) != odor_sequence[env*number_of_odors+current_odor_position-1]): #don't repeat the last odor
                    odor_sequence[env*number_of_odors+current_odor_position] = int(odor[column])  #save this odor in the sequence
                    current_odor_position = current_odor_position+1
print 'The odors were presented in this sequence (4 odors per environment):'
print odor_sequence


event_data_averaged_per_environment = np.empty((event_data.shape[0],number_of_odors*number_of_environments),dtype='int')

for env in range(0,number_of_environments):
    environment_start_lap = environment_transitions[env]
    environment_end_lap = environment_transitions[env+1]
    environment_lap_count = environment_end_lap - environment_start_lap
    for row in range(0,event_data_averaged_per_environment.shape[0]):
        for column in range(env*number_of_odors,(env+1)*number_of_odors):
            laps_with_events = 0
            for lap in range (environment_start_lap,environment_end_lap):
                if(event_data_for_plotting[row][lap*number_of_odors + column%number_of_odors] > 0):
                    laps_with_events = laps_with_events + 1
            event_data_averaged_per_environment[row][column] = ((laps_with_events*100) / environment_lap_count)

print 'Sample of summed event values'     
print event_data_averaged_per_environment[0,:]

###############################################################################
###############################################################################
###################### now we plot some good nice heatmaps ####################
###############################################################################
###############################################################################

def generate_plots(complete_data_array):
    
    

    figs = []
    
    for odor in range(0,complete_data_array.shape[1]):
        
        data_array = complete_data_array[np.argsort(complete_data_array[:,odor],kind='quicksort')]
        
        fig = plt.figure()
        fig.set_rasterized(True)
        fig.suptitle('Plot of %d sorted cells' %total_number_of_cells)
        #fig.set_size_inches(10,2) 
        
        odor_response_ticks = [10,20,30,40,50,60,70,80,90,100]
        
        ax1 = plt.subplot2grid((number_of_environments,number_of_environments), (0,0), rowspan=number_of_environments)
        heatmap1 = ax1.pcolor(data_array[:,0:4], cmap=plt.cm.Blues)
        plt.colorbar(heatmap1,aspect=30, ticks=odor_response_ticks)
        od = odor_sequence[0:4]
        row_labels = list(' %d %d %d %d' %(od[0],od[1],od[2],od[3]))
        ax1.set_xticklabels(row_labels, minor=False)
        #the x and y axis labels of ax1 are shared by all other subplots
        ax1.xaxis.tick_bottom()
        ax1.set_xlabel('Odor')
        ax1.set_ylabel('Cell#')

        for env in range (1,number_of_environments):
            ax = plt.subplot2grid((number_of_environments,number_of_environments), (0,env), rowspan=number_of_environments, sharey=ax1)
            heatmap = ax.pcolor(data_array[:,env*number_of_odors:(env+1)*number_of_odors], cmap=plt.cm.Blues) 
            color_legend = plt.colorbar(heatmap,aspect=30,ticks=odor_response_ticks)
            color_legend.ax.tick_params(labelsize=8) 
            plt.setp(ax.get_yticklabels(), visible=False)
            ax.set_xlabel('Odor')
            od = odor_sequence[env*number_of_odors:(env+1)*number_of_odors]
            row_labels = list(' %d %d %d %d' %(od[0],od[1],od[2],od[3]))
            ax.set_xticklabels(row_labels, minor=False) 
            fig.add_subplot(ax)
        
        
        


        plt.ylim (0,total_number_of_cells)
        
        #suppress the y labels of all subplots except ax1
#        yticklabels = ax2.get_yticklabels()+ax3.get_yticklabels()+ax4.get_yticklabels()  
#        plt.setp(yticklabels, visible=False)
        
        #can be commented out to stop showing all plots in the console
        plt.show()

        figs.append(fig)
        plt.close()
        
    if len(figs) > 0:
        pdf_name = file_path.replace(".csv", ".pdf")
        pp = PdfPages(pdf_name)
        for fig in figs:
            pp.savefig(fig,dpi=300)
        pp.close() 

###############################################################################
################# just a final touch of the magic wand ########################
###############################################################################
generate_plots(event_data_averaged_per_environment)