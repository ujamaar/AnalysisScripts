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
print odor[0:15]


#delete the desired number of rows/columns in the desired axis
event_data = np.delete(event_data, (0,1,2,3,4,5,6,7), axis=0)
total_number_of_cells = len(event_data)
print 'There are %d cells to be plotted' %total_number_of_cells

#print a portion of the event data just to check
print event_data[0:10,0:10]



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
        print 'Processing cell# %d'%row
    while (column < len(lap_count)):
        #print '-----------------------This lap starts at %d --------------------' %(column)
        if(lap_count[column] > lap_count[column-2]):
            current_lap = current_lap + 1
            current_odor = -1
            new_lap_starts_in_this_column = column
            #print 'new lap starts at %d' %new_lap_starts_in_this_column
        
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
                    #print 'event %d'%column
                event_data_for_plotting[row][current_lap*number_of_odors + current_odor] = odor_response
            else:
                column = column + 1
                #print 'still trying odor response for column %d' %current_odor_column
            
            #odor_column = current_odor_column
            #lap_column = odor_column
            #print 'new odor starting at column: %d' %odor_column   
        else:
            column = column+1
        #print 'next lap starts at %d' %column
                

event_data_averaged_over_laps = np.empty((event_data.shape[0],number_of_odors))

for row in range(0,event_data_averaged_over_laps.shape[0]):
    for column in range(0,event_data_averaged_over_laps.shape[1]):
        summed_value = 0.00
        total_lap_count = int(total_laps)-1
        for lap in range (0,total_lap_count):
            summed_value = summed_value + event_data_for_plotting[row][lap*number_of_odors + column]
        event_data_averaged_over_laps[row][column] = summed_value

        
print event_data_averaged_over_laps[0:10,0:10]



###############################################################################
###############################################################################













################################################################################
################################################################################
##if there are too many time points, condense the data points to keep the array size within a sane range
##lets say the size of the figure will be adjusted to always have 100 time points
#number_of_odors = 4
#event_data_for_plotting = np.empty((event_data.shape[0],total_laps*number_of_odors)) 
#
#
#
#
#for row in range(0,event_data.shape[0]):
#    current_lap = 0
#    lap_column = 1
#    print 'Processing cell# %d'%row
#    while (lap_column < len(lap_count)):
#        print 'This lap starts at %d' %lap_column
#        if(lap_count[lap_column] > lap_count[lap_column-2]):
#            current_lap = current_lap + 1
#            print 'moved on to a new lap here------------------------'
#            current_odor = 0
#            #lap_column = lap_column + 1
#        odor_column = lap_column
#        current_odor = -1
#        print 'Current lap is %d' %current_lap
#        
#        while((odor_column < len(lap_count)-1) & (lap_count[odor_column] == lap_count[odor_column-1])):                      #for each lap
#            if((odor[odor_column]>0.00) & (odor[odor_column]!=odor[odor_column-1])):
#                current_odor = current_odor + 1
#                #print 'Current odor is %d ' %current_odor
#                odor_column = odor_column + 1
#            current_odor_column = odor_column
#            print 'Current odor is %d ' %current_odor
#            
#            if(odor[current_odor_column] > 0.00):
#                print 'this column has odor data %d' %current_odor_column
#                odor_response = 0
#                while((current_odor_column < len(lap_count)-1) & (odor[current_odor_column]==odor[current_odor_column-1])):         #for each odor in each lap
#                    odor_response = odor_response + event_data[row][current_odor_column]
#                    current_odor_column = current_odor_column + 1
#                event_data_for_plotting[row][current_lap*number_of_odors + current_odor] = odor_response
#            else:
#                current_odor_column = current_odor_column + 1
#                #print 'still trying odor response for column %d' %current_odor_column
#            
#            odor_column = current_odor_column
#            lap_column = odor_column
#            #print 'new odor starting at column: %d' %odor_column   
#        else:
#            lap_column = odor_column+1
#        print 'next lap starts at %d' %lap_column
#                
#        
#        
#print event_data_for_plotting[0:10,0:10]
#
#
#
################################################################################
################################################################################



figs = []

cells_in_one_plot = 300
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
     
    plot_data = event_data_averaged_over_laps[last_cell_index:last_cell_index + cells_in_one_plot,:]
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
