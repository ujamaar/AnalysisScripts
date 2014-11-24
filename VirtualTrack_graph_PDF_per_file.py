# -*- coding: utf-8 -*-
"""
Created on Wed Jul 30 18:52:38 2014

@author: njoshi
"""
#something for inspiration: http://matplotlib.org/examples/pylab_examples/multiple_yaxis_with_spines.html
#more inspiration: https://datasciencelab.wordpress.com/2013/12/21/beautiful-plots-with-pandas-and-matplotlib/

import os
from pylab import *
from matplotlib.backends.backend_pdf import PdfPages
import re

directory_path ='C:/Users/axel/Desktop/test_data'
#directory_path ='//losonczy-server/walter/Virtual_Odor/behavior_data/wfnjC8'

#directory path format for mac computers:
#directory_path ='/Users/njoshi/Documents/nwp_test_data'
#directory_path ='\\losonczy-server\walter\Virtual_Odor\behavior_data\wfnjC3\wfnjC8'

def generate_graph(filename):
    
    data = [pylab.loadtxt(filename, delimiter=',',skiprows=2)]
    datalist = data[0]
    
    time = []
    valves = []
    licks = []
    #lick_count = []
    rewards = []	
    distance = []
    #total_distance = []
    speed = []
    #lick_rate = []
    reward_availability = []
    initial_drop = []
    lap_count = []
    
    #read data points from the tuple into lists, which are easier to work with
    for row in range(0,len(datalist)):
        time.append(datalist[row][0])
        valves.append(datalist[row][1])    
        licks.append(datalist[row][2])
        #lick_count.append(datalist[row][3])
        rewards.append(datalist[row][4])
        distance.append(datalist[row][6])
        #total_distance.append(datalist[row][7])
        reward_availability.append(datalist[row][8])
        initial_drop.append(datalist[row][9])
        lap_count.append(int(datalist[row][15]))
        speed.append(0) #make a list full of 0's, same in size as the other lists
        #lick_rate.append(0)
    
    
    s1 = float(distance[0])
    s2 = 0.0
    t1 = float(time[0])
    t2 = 0.0
    #l1 = float(lick_count[0])
    #l2 = 0.0
    
    current_speed = 0.0
    #current_lick_rate = 0.0    
    
    for line in range(0,len(datalist)):
        #read current distance and time
        t2 = float(time[line])
        s2 = float(distance[line])
        #l2 = float(lick_count[line])
        
        #if there is no change in time, the speed remains unchanged
        #speed is calculated for every 2000 ms window in this case
        if (t2 - t1 > 1000):
            current_speed = (s2 - s1)/(t2 - t1) #speed is in m/s
            #current_lick_rate = ((l2 - l1)*1000)/(t2-t1)
            t1 = t2
            s1 = s2
            #l1 = l2
        else:
            current_speed = 0
            #current_lick_rate = 0
                
        speed[line] = current_speed
        #lick_rate[line] = current_lick_rate
    

    figs = []
    
    print max(lap_count)
    for i in range(0,max(lap_count)+1):
        print i
        
        lap_valves = []
        lap_licks = []
        lap_rewards = []
        lap_distance = []
        lap_speed = []
        lap_initial_drop = []
        lap_reward_availability = []
        
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
        
        x6 = []
        y6 = []

        for row in range(0,len(lap_count)):
            if lap_count[row] == i:
                lap_valves.append(valves[row])
                lap_licks.append(licks[row])
                lap_rewards.append(rewards[row])
                lap_distance.append(distance[row])
                lap_speed.append(speed[row])
                lap_initial_drop.append(initial_drop[row])
                lap_reward_availability.append(reward_availability[row])

        for row in range(0,len(lap_distance)):
            if lap_speed[row] != 0:
                x1.append(lap_distance[row])
                y1.append(lap_speed[row])

            if lap_rewards[row] == 1:
                x2.append(lap_distance[row])
                y2.append(lap_rewards[row])                

            if lap_licks[row] == 1:
                x3.append(lap_distance[row])
                y3.append(lap_licks[row])

            if lap_initial_drop[row] == 1:
                x5.append(lap_distance[row])
                y5.append(lap_initial_drop[row] * 5) 


        for row in range(1,len(lap_distance)):        
            if lap_valves[row] != lap_valves[row - 1]:
                x4.append(lap_distance[row - 1])
                y4.append(lap_valves[row - 1])  
                x4.append(lap_distance[row])
                y4.append(lap_valves[row]) 
            
            if lap_reward_availability[row] != lap_reward_availability[row - 1]:
                x6.append(lap_distance[row-1])
                y6.append(lap_reward_availability[row-1])        
                x6.append(lap_distance[row])
                y6.append(lap_reward_availability[row])  
        
        x4.append(lap_distance[len(lap_distance)-1])
        y4.append(lap_valves[len(lap_distance)-1])
        x4.append(lap_distance[len(lap_distance)-1])
        y4.append(0)
        
#now plotting the data in a figure (with 4 subplots in this case):
        
        fig = figure()
        
        subplots_adjust(hspace=0)
                       
        
        ax1 = subplot(411)
        ax1.plot(x1,y1,'b-', linewidth = 0.01)
        ax1.vlines(x6,0,y6, color ='r', linewidth = 0.01)
        ax1.set_ylabel('Speed(m/s)', fontsize='xx-small')
        #ax1.set_title(filename, fontsize=10)
        xlim(0,max(distance)); 
        ylim(0,0.8);      

        ax2 = subplot(412, sharex=ax1)
        ax2.vlines(x2,0,y2, color='r', linewidth = 0.01)
        ax2.set_ylabel('Rewards', fontsize='xx-small')        
        
        ax3 = subplot(413, sharex=ax1)
        ax3.vlines(x3,0,y3,color = 'g', linewidth = 0.01)
        ax3.vlines(x6,0,y6, color ='r', linewidth = 0.01)
        ax3.set_ylabel('Licks', fontsize='xx-small')
        ylim(0,1)
        
        ax4 = subplot(414, sharex=ax1)
        ax4.plot(x4,y4,'r-', linewidth = 0.01)
        ax4.vlines(x5,0,y5, color = 'b', linewidth = 0.1)
        ax4.set_ylabel('Odor', fontsize='xx-small')
        ax4.set_xlabel('Distance along the virtual track(mm)', fontsize='xx-small')
        xlim(0,max(distance));
        ylim(0,6);
  
        for item in ([ax1.title, ax1.xaxis.label, ax1.yaxis.label] + ax1.get_xticklabels() + ax1.get_yticklabels()):
            item.set_fontsize(5)
        
        xticklabels = ax1.get_xticklabels()+ax2.get_xticklabels()+ax3.get_xticklabels()  
        setp(xticklabels, visible=False)

        yticklabels = ax2.get_yticklabels()+ax3.get_yticklabels()+ax4.get_yticklabels()  
        setp(yticklabels, visible=False)
        
        #to set line width of the axes
        for axis in ['top','bottom','left','right']:
          ax1.spines[axis].set_linewidth(0.01)
          ax1.spines[axis].set_linewidth(0.01)
          ax2.spines[axis].set_linewidth(0.01) 
          ax3.spines[axis].set_linewidth(0.01) 
          ax4.spines[axis].set_linewidth(0.01)
          #ax4.spines[axis].set_hatch('x')
        
        figs.append(fig)
        
        #plt.annotate()
        plt.close()

    if len(figs) > 0:
		pdf_name = filename + '.pdf'
		pp = PdfPages(pdf_name)
		
		for fig in figs:
			pp.savefig(fig)
		pp.close()    

#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

file_names = [os.path.join(directory_path, f)
    for dirpath, dirnames, files in os.walk(directory_path)
    for f in files if f.endswith('.csv')]
file_names.sort(key=natural_key)

#now generate a pdf file for each .csv file
for filez in file_names:
        print filez
        #check whether there is already a pdf
        if os.path.isfile(filez + '.pdf'):
            print 'A pdf already exists for this file. Delete the pdf to generate a new one.'
        else:
            generate_graph(filez)
