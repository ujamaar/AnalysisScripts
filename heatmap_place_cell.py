#based on source: http://stackoverflow.com/questions/14391959/heatmap-in-matplotlib-with-pcolor
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

file_path = '/Users/njoshi/Desktop/test_data/sample_events_for_place_cell.csv'

event_data = np.loadtxt(file_path, dtype='float', delimiter=',')
#event_data = event_data[0:22,0:5]
#to plot time as x-axis, transpose the whole array
event_data = event_data.transpose()
print "Events array size is: (%d ,%d)" %(event_data.shape[0], event_data.shape[1])

odor = event_data[2,:]
lap_count = event_data[6,:]
total_laps = max(lap_count) + 1
distance = event_data[5,:]
track_length = max(4500,int(max(distance)))
environment = event_data[7,:]
number_of_environments = int(max(environment))
print 'There are %d laps in this recording' %total_laps
print 'There are %d environments in this recording' %number_of_environments
#print odor[0:15]


#delete the desired number of rows/columns in the desired axis
#column 2 = odor
#column 5 = distance
#column 6 = lap
#column 7 = environment
event_data = np.delete(event_data, (0,1,2,3,4,5,6,7,8), axis=0)
total_number_of_cells = len(event_data)
print 'There are %d cells to be plotted' %total_number_of_cells


###############################################################################
#if there are too many time points, condense the data points to keep the array size within a sane range
#lets say the size of the figure will be adjusted to always have 100 time points
distance_bin = 50  #in mm (5cm)
number_of_distance_bins = track_length / distance_bin
event_data_for_plotting = np.empty((event_data.shape[0],number_of_environments*number_of_distance_bins)) 


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



###############################################################################
###################### now we plot some good nice heatmaps ####################
###############################################################################

def generate_plots(data_array,sorted_column):

    figs = []
    
    fig = plt.figure()
    fig.suptitle('Plot of %d sorted cells'%total_number_of_cells, fontsize=12)
    ax1 = plt.subplot2grid((5,5), (0,0), colspan=5, rowspan=5)
        
    #now make the actual plot using pcolor
    event_heatmap = ax1.pcolor(data_array, cmap=plt.cm.Blues)
    
    ax1.xaxis.tick_bottom()

    ax1.set_xlabel('Odor')
    ax1.set_ylabel('Cell#')
    #plt.xlim(0,plot_data.shape[1])
    plt.ylim (0,total_number_of_cells)
    
    row_labels = list(' 1 2 3 4')
    ax1.set_xticklabels(row_labels, minor=False)
    
    #can be commented out to stop showing all plots in the console
    plt.show()
    
    figs.append(fig)
    plt.close()
        
    if len(figs) > 0:
        pdf_name = file_path.replace(".csv", ".pdf")
        pp = PdfPages(pdf_name)
        for fig in figs:
            pp.savefig(fig)
        pp.close() 

###############################################################################
###############################################################################
###############################################################################

#sort the cells according to size of summed events along the desired odor column
sort_column = 0
now_plot_this = event_data_averaged_over_laps[np.argsort(event_data_averaged_over_laps[:,sort_column],kind='quicksort')]

print 'Sample of summed event values'     
print now_plot_this[0:10,0:10]

generate_plots(now_plot_this,sort_column)
