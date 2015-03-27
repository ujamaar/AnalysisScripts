#based on source: http://stackoverflow.com/questions/14391959/heatmap-in-matplotlib-with-pcolor
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

event_data = np.loadtxt('/Users/njoshi/Desktop/test_data/traces_smaller.csv', dtype='float', delimiter=',')
#event_data = event_data[0:22,0:5]
#to plot time as x-axis, transpose the whole array
event_data = event_data.transpose()
print "Events array size is: (%d ,%d)" %(event_data.shape[0], event_data.shape[1])

#odors = event_data[2,:]
#print odors[0:100]

#delete the desired number of rows/columns in the desired axis
event_data = np.delete(event_data, (0), axis=0)
total_number_of_cells = len(event_data)
print 'There are %d cells to be plotted' %total_number_of_cells

#print a portion of the event data just to check
print event_data[0:10,1]


#if there are too many time points, condense the data points to keep the array size within a sane range
#lets say the size of the figure will be adjusted to always have 100 time points
max_time_points_in_plot = 10
event_data_for_plotting = np.empty((event_data.shape[0],max_time_points_in_plot)) 

if(event_data.shape[1] > max_time_points_in_plot):
    points_to_be_condensed = event_data.shape[1] / max_time_points_in_plot
    print 'Sum every %d event values' %points_to_be_condensed
     
    for row in range(0,event_data_for_plotting.shape[0]):        
        for column in range(0, event_data_for_plotting.shape[1]):
            start_block = column * points_to_be_condensed
            end_block = (column + 1) * points_to_be_condensed
            summed_value = 0
            for block_col in range(start_block, end_block):
                summed_value = summed_value + event_data[row][block_col]
            event_data_for_plotting[row][column] = summed_value
else:
    event_data_for_plotting = event_data
    print 'Didn not need to condense values'

#print event_data_for_plotting[0:10,0:10]



figs = []

cells_in_one_plot = 100
last_cell_index = 0

keep_plotting_figures = True

while(keep_plotting_figures):    
    fig = plt.figure()
    #fig.set_size_inches(10,2)    
    ax = fig.add_subplot(1, 1, 1)
    fig.subplots_adjust(hspace=0)
    
    if(last_cell_index + cells_in_one_plot >= total_number_of_cells):
        cells_in_one_plot =  total_number_of_cells - last_cell_index
        keep_plotting_figures = False
     
    plot_data = event_data_for_plotting[last_cell_index:last_cell_index + cells_in_one_plot,:]
    last_cell_index = last_cell_index + cells_in_one_plot
    
    #now make the actual plot using pcolor
    event_heatmap = ax.pcolor(plot_data, cmap=plt.cm.Blues)
    
    ax.xaxis.tick_bottom()
    ax.set_title('Plot of cells from # %d to %d '%(last_cell_index - cells_in_one_plot,last_cell_index))
    ax.set_xlabel('time')
    ax.set_ylabel('Cell#')
    plt.xlim(0,plot_data.shape[1])
    plt.ylim (0 , cells_in_one_plot)
    
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