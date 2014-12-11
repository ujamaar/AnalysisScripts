#based on source: http://stackoverflow.com/questions/14391959/heatmap-in-matplotlib-with-pcolor
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

event_data = np.loadtxt('/Users/njoshi/Desktop/test_data/behavior_and_imaging_combined.csv', dtype='float', delimiter=',')
#event_data = event_data[0:22,0:5]
#to plot time as x-axis, transpose the whole array
event_data = event_data.transpose()
print "Events array size is: (%d ,%d)" %(event_data.shape[0], event_data.shape[1])

odor = event_data[2,:]
lap_count = event_data[6,:]
total_laps = max(lap_count) + 1
print 'There are %d laps in this trial' %total_laps
#print odor[0:15]


#delete the desired number of rows/columns in the desired axis
event_data = np.delete(event_data, (0,1,2,3,4,5,6,7), axis=0)
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



###############################################################################
###################### now we plot some good nice heatmaps ####################
###############################################################################

def generate_plots(data_array,sorted_column):

    figs = []
    
    #you can choose to limit how many cells get plotted in one graph
    cells_in_one_plot = total_number_of_cells
    last_cell_index = 0
    
    keep_plotting_figures = True
    
    while(keep_plotting_figures):    
        fig = plt.figure()
        #fig.set_size_inches(10,2) 
        #ax1 = fig.add_subplot(1, 1, 1)
        #ax2 = fig.add_subplot(1, 1, 1)
        ax1 = plt.subplot2grid((3,4), (0,0), rowspan=3)
#        ax2 = plt.subplot2grid((3,4), (0,1), rowspan=3)
#        ax3 = plt.subplot2grid((3,4), (0,2), rowspan=3)
#        ax4 = plt.subplot2grid((3,4), (0,3), rowspan=3)
        
        
        if(last_cell_index + cells_in_one_plot >= total_number_of_cells):
            cells_in_one_plot =  total_number_of_cells - last_cell_index
            keep_plotting_figures = False
         
        plot_data = data_array[last_cell_index:last_cell_index + cells_in_one_plot,:]
        last_cell_index = last_cell_index + cells_in_one_plot
        
        #now make the actual plot using pcolor
        event_heatmap = ax1.pcolor(plot_data, cmap=plt.cm.Blues)
        
        ax1.xaxis.tick_bottom()
        ax1.set_title('Plot of cells from # %d to %d '%(last_cell_index - cells_in_one_plot,last_cell_index))
        ax1.set_xlabel('Odor')
        ax1.set_ylabel('Cell#')
        #plt.xlim(0,plot_data.shape[1])
        plt.ylim (0 , cells_in_one_plot)
        
        row_labels = list(' 1 2 3 4')
        ax1.set_xticklabels(row_labels, minor=False)
        
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
###############################################################################
###############################################################################

#sort the cells according to size of summed events along the desired odor column
sort_column = 0
now_plot_this = event_data_averaged_over_laps[np.argsort(event_data_averaged_over_laps[:,sort_column],kind='quicksort')]

print 'Sample of summed event values'     
print now_plot_this[0:10,0:10]

generate_plots(now_plot_this,sort_column)
