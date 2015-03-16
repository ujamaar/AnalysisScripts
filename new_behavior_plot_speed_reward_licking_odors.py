# -*- coding: utf-8 -*-
"""
Created on Wed Jul 30 18:52:38 2014

@author: njoshi
"""
#something for inspiration: http://matplotlib.org/examples/pylab_examples/multiple_yaxis_with_spines.html
import numpy
import os
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import re

directory_path ='/Users/njoshi/Desktop/events_test'
#directory_path ='C:/cygwin/home/axel/RotaryDisc_CABA/Recordings/nwp68/nwp68_2014_11_05'
#\\losonczy-server\walter\Virtual_Odor\behavior_data\wfnjC3\wfnjC3_2014_10_06

def generate_graph(filename,track_length):
    
    behavior_data = numpy.loadtxt(filename, dtype='int', delimiter=',',skiprows=2)

    #column 0 = frame number
    #column 1 = time
    #column 2 = odor
    #column 3 = licks
    #column 4 = rewards
    #column 5 = initial drop
    #column 6 = reward window
    #column 7 = distance
    #column 8 = total distance
    #column 9 = lap
    #column 10 = environment

###################################################################      
#Calculate speed(measured as time taken to travel each 50mm stretch of the track):
###################################################################

#    #calculate speed per 50mm stretch of the track########################################
#
#    s1 = 0.00
#    s2 = 0.00
#    t1 = 0.00
#    t2 = 0.00
##    last_line_fill = 0
#    speed = numpy.zeros(len(behavior_data),dtype='float')
#   
#    current_speed = 0.00
#    #current_lick_rate = 0.0    
#    
#    for line in range(0,len(behavior_data)):
#        #read current distance and time
#        s2 = behavior_data[line][7]
#        #sanity_check = raw_behavior[line-1][6]
#        #if there is no change in time, the speed remains unchanged
#        #speed is calculated for every 500 ms window in this case
#        if (s2 >= ((int(s1/100.00) + 1)*100.00)):# and (abs(s2-sanity_check) < 20.00)):
#            t2 = behavior_data[line-1][1]
#            s2 = behavior_data[line-1][7]
#            current_speed = (s2 - s1)*100/(t2 - t1) #speed is in cm/s
#            
#            speed[line-1] = current_speed
#            
#            t1 = behavior_data[line][1]
#            s1 = behavior_data[line][7]
#            
##            for blank_line in range(last_line_fill,line):
##                speed[blank_line] = current_speed
##            last_line_fill = line
#        #at the end of reward region, when the distance measurement resets to zero
#        elif(s2 < s1 and s1-s2 > 100.00):
#            t2 = behavior_data[line-1][1]
#            s2 = behavior_data[line-1][7]          
#            current_speed = (s2 - s1)*100/(t2 - t1) #speed is in cm/s
#
#            speed[line-1] = current_speed
##            for blank_line in range(last_line_fill,line):
##                speed[blank_line] = current_speed
##            last_line_fill = line            
#            t1 = behavior_data[line][1]
#            s1 = behavior_data[line][7]
#        #at the end of the recording
#        elif(line == len(behavior_data)-1):
#            t2 = behavior_data[line][1]
#            s2 = behavior_data[line][7]          
#            current_speed = (s2 - s1)*100/(t2 - t1) #speed is in cm/s
#
#            speed[line-1] = current_speed
##            for blank_line in range(last_line_fill,line+1):
##                speed[blank_line] = current_speed          
#
####################################################################      
##done calculating speed(measured as time taken to travel each 50mm stretch of the track):
####################################################################


###################################################################      
#Calculate speed(measured as distance traveled every 500ms):
###################################################################

    #calculate speed every 500ms
    s1 = 0.00    
    s2 = 0.00 #float(behavior_data[0,7])
    t1 = 0.00 
    t2 = 0.00 #float(behavior_data[0,1])
    
    speed = numpy.zeros(behavior_data.shape[0],dtype='float')

    for line in range(0,behavior_data.shape[0]):
        #read current distance
        t2 = float(behavior_data[line][1])
        s2 = float(behavior_data[line][7])
        
        #if there is no change in time, the speed remains unchanged
        #speed is calculated for every 2000 ms window in this case
        if (t2 - t1 > 500 and abs(s2-s1) < 2000):
            t2 = behavior_data[line-1][1]
            s2 = behavior_data[line-1][7]
            speed[line-1] = (s2 - s1)*100.00/(t2 - t1) #speed is in cm/s
            t1 = behavior_data[line][1]
            s1 = behavior_data[line][7]
        #at the end of reward region, when the distance measurement resets to zero
        elif(abs(s2-s1) > 2000): #to reset values when a new track starts
            t2 = behavior_data[line-1][1]
            s2 = behavior_data[line-1][7]
            speed[line-1] = (s2 - s1)*100.00/(t2 - t1) #speed is in cm/s
            speed[line] = (s2 - s1)*100.00/(t2 - t1) #speed is in cm/s
            t1 = behavior_data[line][1]
            s1 = behavior_data[line][7]
        #at the end of the recording
        elif(line == len(behavior_data)-1): 
            speed[line] = (s2 - s1)*100.00/(t2 - t1) #speed is in cm/s      

###################################################################      
#done calculating speed(measured as distance traveled every 500ms):
###################################################################
                

###################################################################      
#for each lap, generate the data points to be plotted:
###################################################################
    
    figs = []

    
    #get the total number of laps in this recording
    lap_count = numpy.int(max(behavior_data[:,9])) + 1
    print 'Total number of laps: %d' %lap_count

    color_options = ['y','b','g','r','c','m']   
    
    #now generate the plots    
    for current_lap in range(0,lap_count):
        time_data_point = time.time()
        print current_lap+1

        x1 = []
        y1 = []
        
        x2 = []
        y2 = []
        
        x3 = []
        y3 = []
        
        x4 = []
        y4 = []
        
        x5 = []
        y5 = []
        
        last_row_in_current_lap = 0
        for row in range(1,len(behavior_data)):
            if (behavior_data[row][9] == current_lap and speed[row] != speed[row-1]):
                #speed vs. distance
                if speed[row] != 0:
                    x1.append(behavior_data[row][7])
                    y1.append(speed[row])

            if (behavior_data[row][9] == current_lap):                
                #rewards vs. distance
                if behavior_data[row][4] > behavior_data[row-1][4]:
                    x2.append(behavior_data[row][7])
                    y2.append(behavior_data[row][4])
                        
                #licks vs. distance
                if behavior_data[row][3] > behavior_data[row-1][3]:
                    x3.append(behavior_data[row][7])
                    y3.append(behavior_data[row][3])

                #odor valves vs. distance      
                if behavior_data[row][2] != behavior_data[row-1][2]:
                    #x4.append(behavior_data[row-1][7])
                    #y4.append(behavior_data[row-1][2])  
                    x4.append(behavior_data[row][7])
                    y4.append(behavior_data[row][2]) 

                #initial drop vs. distance    
                if behavior_data[row][5] > behavior_data[row-1][5]:
                    x5.append(behavior_data[row][7])
                    y5.append(behavior_data[row][5] * 100)
                
                last_row_in_current_lap = row
        
        
###################################################################      
#now plot the data in a figure (with 4 subplots in this case):
###################################################################


        time_figure_plot = time.time()         
        fig = plt.figure()        
        fig.subplots_adjust(hspace=0)
#        fig.set_rasterized(True)
        plt.figtext(0.45,0.96, "Lap: %s"%(current_lap+1), fontsize='large', color='k', ha ='left') 

        #print x1
        #print y1                       
        ax1 = plt.subplot(311)
        ax1.plot(x1,y1,'b-', linewidth = 0.01)
        for odor in range(0,len(x4)/2):
            #shade the odor region in a light color
            ax1.axvspan(x4[odor*2], x4[odor*2+1], facecolor=color_options[y4[odor*2]], alpha=0.1,linewidth=0.1)
            
            #label the odor numbers just above the plot in red color          
            if(x4[odor*2] % (track_length/4 - 100) < 200):
                plt.figtext(0.3,0.91, "%s"%y4[odor*2], fontsize='large', color='r', ha ='left')
            elif(x4[odor*2] % (track_length/2 - 100) < 200):
                plt.figtext(0.46,0.91, "%s"%y4[odor*2], fontsize='large', color='r', ha ='left')
            elif(x4[odor*2] % ((3*track_length)/4 - 100) < 200):
                plt.figtext(0.62,0.91, "%s"%y4[odor*2], fontsize='large', color='r', ha ='left')  

        if len(x5) > 0:
            ax1.vlines(x5,0,y5, color = 'r', linewidth = 0.01) #to mark the presentation of initial drop
        else:
            ax1.vlines(track_length,0,100, color = 'k', linestyle='dotted', linewidth = 0.01) #else just draw a black line to mark start of reward window
#        if(behavior_data[last_row_in_current_lap][7] > 4000):
        ax1.vlines(behavior_data[last_row_in_current_lap][7],0,100, color = 'k', linestyle='solid', linewidth = 0.05) #to mark end of the track
        ax1.set_ylabel('Speed(cm/s)', fontsize='xx-small')
        ax1.tick_params(axis='both', which='major', labelsize=5)
        #ax1.set_title(filename, fontsize=10)
        plt.xlim(0,track_length + track_length/4)
        plt.ylim(0,100)


        ax2 = plt.subplot(312, sharex=ax1)
        ax2.vlines(x2,0,y2, color='r', linewidth = 0.01)
        for odor in range(0,len(x4)/2):
            ax2.axvspan(x4[odor*2], x4[odor*2+1], facecolor=color_options[y4[odor*2]], alpha=0.1,linewidth=0.1)
        ax2.set_ylabel('Rewards', fontsize='xx-small')
        plt.ylim(0,1)      

       
        ax3 = plt.subplot(313, sharex=ax1)
        ax3.vlines(x3,0,y3,color = 'g', linewidth = 0.01)
        #ax3.vlines(x6,0,y6, color ='r', linewidth = 0.01)
        for odor in range(0,len(x4)/2):
            ax3.axvspan(x4[odor*2], x4[odor*2+1], facecolor=color_options[y4[odor*2]], alpha=0.1,linewidth=0.1)
        ax3.set_ylabel('Licks', fontsize='xx-small')
        ax3.set_xlabel('Distance along the virtual track(mm)', fontsize='small')
        plt.xlim(0,track_length + track_length/4)
        plt.ylim(0,1)
                
        xticklabels = ax1.get_xticklabels()+ax2.get_xticklabels() #+ax3.get_xticklabels()  
        plt.setp(xticklabels, visible=False)

        yticklabels = ax2.get_yticklabels()+ax3.get_yticklabels() #+ax4.get_yticklabels()  
        plt.setp(yticklabels, visible=False)
        
        #to set line width of the axes
        for axis in ['top','bottom','left','right']:
          ax1.spines[axis].set_linewidth(0.01)  
          ax2.spines[axis].set_linewidth(0.01) 
          ax3.spines[axis].set_linewidth(0.01)  
        
        figs.append(fig)
        
        #plt.annotate()
        plt.close()

        #time_done_with_this_lap = 
        print 'time for preparing data = %f'%(time_figure_plot - time_data_point)
        print 'time for plotting  data = %f'%(time.time() - time_figure_plot)
###################################################################      
#Save all plots in a pdf file in the same folder as the source data file:
###################################################################

    pdf_name = filename.replace(".csv","_behavior_plots.pdf")
    pp = PdfPages(pdf_name)    
    for fig in figs:
        pp.savefig(fig)#, dpi=1000, 
    pp.close()

#to make sure that the files are processed in the proper order
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

def main():
    file_names = [os.path.join(directory_path, f)
        for dirpath, dirnames, files in os.walk(directory_path)
        for f in files if f.endswith('.csv')]
    file_names.sort(key=natural_key)
    
    #now generate a pdf file with all the plots (one plot for each file)
    for filez in file_names:
            print "File to be processed: " + filez
            track_length = 4000
            generate_graph(filez,track_length)

main()