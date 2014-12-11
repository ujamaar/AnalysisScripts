#based on source: http://stackoverflow.com/questions/14391959/heatmap-in-matplotlib-with-pcolor
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

event_data = np.loadtxt('/Users/njoshi/Desktop/test_data/behavior_and_imaging_combined.csv', dtype='float', delimiter=',')
#event_data = event_data[0:22,0:5]
#to plot time as x-axis, transpose the whole array
event_data = event_data.transpose()
print "Events array size is: (%d ,%d)" %(event_data.shape[0], event_data.shape[1])

distance = event_data[5,:]
lap_count = event_data[6,:]
environment = event_data[7,:]
total_laps = max(lap_count) + 1
print 'There are %d laps in this trial' %total_laps
#print odor[0:15]


#delete the desired number of rows/columns in the desired axis
#column 2 = odor
#column 5 = distance
#column 6 = lap
#column 7 = environment
event_data = np.delete(event_data, (0,1,2,3,4,5,6,7,8), axis=0)
total_number_of_cells = len(event_data)
print 'There are %d cells to be plotted' %total_number_of_cells

#print a portion of the event data just to check
#print event_data[0:10,0:10]

###############################################################################
#if there are too many time points, condense the data points to keep the array size within a sane range
#lets say the size of the figure will be adjusted to always have 100 time points
number_of_odors = 4
event_data_for_plotting = np.empty((event_data.shape[0],total_laps*number_of_odors)) 

for row in range(0,event_data.shape[0]):
    current_lap = 0
    current_odor = -1
    new_lap_starts_in_this_column = 0
    odor_starts_in_this_column = 0
    column = 1
    if (row % 20 == 0):
        print 'Processing cell# %d / %d'%(row,total_number_of_cells)
    while (column < len(lap_count)):
        #print '-----------------------This lap starts at %d --------------------' %(column)
        if(lap_count[column] > lap_count[column-2]):
            current_lap = current_lap + 1
            current_odor = -1
            new_lap_starts_in_this_column = column
        
        while((column < len(lap_count)-1) and ((lap_count[column] == lap_count[column-1]) or (column == new_lap_starts_in_this_column))):                      #for each lap
            if((odor[column]>0.00) & (odor[column]!=odor[column-1])):
                current_odor = current_odor + 1
                new_odor_starts_in_this_column = column
                #print 'new odor starts in column %d ' %new_odor_starts_in_this_column
            #print 'Current odor is %d ' %current_odor
            
            if(odor[column] > 0.00):
                #print 'this column has odor data %d' %column
                odor_response = 0
                
                while((column < len(lap_count)) and ((odor[column]==odor[column-1]) or (column == new_odor_starts_in_this_column))):         #for each odor in each lap
                    odor_response = odor_response + event_data[row][column]
                    column = column + 1
                event_data_for_plotting[row][current_lap*number_of_odors + current_odor] = odor_response
            else:
                column = column + 1
        else:
            column = column+1
                
###############################################################################
# now calculate the proportion of laps for each odor that had an event #
###############################################################################

event_data_averaged_over_laps = np.empty((event_data.shape[0],number_of_odors))

for row in range(0,event_data_averaged_over_laps.shape[0]):
    for column in range(0,event_data_averaged_over_laps.shape[1]):
        laps_with_events = 0.00
        total_lap_count = int(total_laps)
        for lap in range (0,total_lap_count-1):
            if(event_data_for_plotting[row][lap*number_of_odors + column] > 0.00):
                laps_with_events = laps_with_events + 1.00
        event_data_averaged_over_laps[row][column] = (laps_with_events / total_lap_count)*100.00

print 'Sample of summed event values'     
print event_data_averaged_over_laps[0:10,0:10]

###############################################################################
###################### now we plot some good nice heatmaps ####################
###############################################################################

def generate_plots(data_array):

    figs = []
        
    fig = plt.figure()
    fig.suptitle('Plot of %d sorted cells'%total_number_of_cells, fontsize=12)
    #fig.set_size_inches(10,2) 
    ax1 = plt.subplot2grid((3,4), (0,0), rowspan=3)
    ax2 = plt.subplot2grid((3,4), (0,1), rowspan=3, sharex=ax1, sharey=ax1)
    ax3 = plt.subplot2grid((3,4), (0,2), rowspan=3, sharex=ax1, sharey=ax1)
    ax4 = plt.subplot2grid((3,4), (0,3), rowspan=3, sharex=ax1, sharey=ax1)
    
    #sort the cells according to their response to an odor     
    plot_data1 = data_array[np.argsort(data_array[:,0],kind='quicksort')]
    plot_data2 = data_array[np.argsort(data_array[:,1],kind='quicksort')]
    plot_data3 = data_array[np.argsort(data_array[:,2],kind='quicksort')]
    plot_data4 = data_array[np.argsort(data_array[:,3],kind='quicksort')]
    
    #now make the actual plot using pcolor
    event_heatmap = ax1.pcolor(plot_data1, cmap=plt.cm.Blues)
    event_heatmap = ax2.pcolor(plot_data2, cmap=plt.cm.Reds)
    event_heatmap = ax3.pcolor(plot_data3, cmap=plt.cm.Greens)
    event_heatmap = ax4.pcolor(plot_data4, cmap=plt.cm.Reds) 
    
    #the x and y axis labels of ax1 are shared by all other subplots
    ax1.xaxis.tick_bottom()
    ax1.set_xlabel('Odor')
    ax1.set_ylabel('Cell#')
    row_labels = list(' 1 2 3 4')
    ax1.set_xticklabels(row_labels, minor=False)

    plt.ylim (0,total_number_of_cells)
    
    #suppress the y labels of all subplots except ax1
    yticklabels = ax2.get_yticklabels()+ax3.get_yticklabels()+ax4.get_yticklabels()  
    plt.setp(yticklabels, visible=False)
    
    #can be commented out to stop showing all plots in the console
    plt.show()
    
    figs.append(fig)
    plt.close()
        
    if len(figs) > 0:
        pdf_name = '/Users/njoshi/Desktop/test_data/test_plot.pdf'
        pp = PdfPages(pdf_name)
        for fig in figs:
            pp.savefig(fig)
        pp.close() 

###############################################################################
###################### just a final touch here ################################
###############################################################################
generate_plots(event_data_averaged_over_laps)
