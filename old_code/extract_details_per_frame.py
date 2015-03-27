import os
from pylab import *
import re

#this script is for combining two behavior data files into one seamlessly
#so that all variables increase naturally in the combined file

#to combine two files, put them in the same folder, and provide 
#the location of this folder in the directory_path below

#make sure that the files are combined in the proper order (displayed in the terminal)


#directory_path ='C:/Users/axel/Desktop/test_data'
#directory_path ='//losonczy-server/walter/Virtual_Odor/behavior_data/wfnjC8'

#directory path format for mac computers:
directory_path ='/Users/njoshi/Desktop/test_data'
#directory_path ='/Volumes/walter/Virtual_Odor/behavior_data/wfnjC8'

def extract_details_per_frame (complete_file):
   
    data = [pylab.loadtxt(complete_file, delimiter=',',skiprows=2)]
    datalist1 = data[0]
      
    time = []
    valves = []
#    licks = []
    lick_count = []
#    rewards = []
    reward_count = []	
    distance = []
#    total_distance = []
#    reward_availability = []
#    initial_drop = []
#    initial_drop_count = []
#    imaging_trigger = []
    ttl_pulse = []
#    ttl_total_count = []
#    lick_rate = []
    lap_count = []
    environment = []

    #read data points from the tuple into lists, which are easier to work with
    for row in range(0,len(datalist1)):
        if(datalist1[row][12] > 0):
            time.append(datalist1[row][0])
            valves.append(datalist1[row][1])    
    #        licks.append(datalist1[row][2])
            lick_count.append(datalist1[row][3])
    #        rewards.append(datalist1[row][4])
            reward_count.append(datalist1[row][5])
            distance.append(datalist1[row][6])
    #        total_distance.append(datalist1[row][7])
    #        reward_availability.append(datalist1[row][8])
    #        initial_drop.append(datalist1[row][9])
    #        initial_drop_count.append(datalist1[row][10])
    #        imaging_trigger.append(datalist1[row][11])
            ttl_pulse.append(datalist1[row][12])
    #        ttl_total_count.append(datalist1[row][13])
    #        lick_rate.append(datalist1[row][14])
            lap_count.append(int(datalist1[row][15]))
            
            if(len(datalist1[row]) == 17):
                environment.append(int(datalist1[row][16]))
            else:
                environment.append(1)


    ##now just save all the lists together in a .csv file
        
    output_filename = complete_file + '_per_frame.csv'
    print "The file with details for each frame is:"
    print output_filename
    big_file = open(output_filename, "a+")
        
    for row in range(0,len(time)):
        new_line = (str(int(ttl_pulse[row]))+','+
                    str(int(time[row]))+','+
                    str(int(valves[row]))+','+
#                    str(int(licks[row]))+','+
                    str(int(lick_count[row]))+','+
#                    str(int(rewards[row]))+','+
                    str(int(reward_count[row]))+','+
                    str(int(distance[row]))+','+
#                    str(int(total_distance[row]))+','+
#                    str(int(reward_availability[row]))+','+
#                    str(int(initial_drop[row]))+','+
#                    str(int(initial_drop_count[row]))+','+
#                    str(int(imaging_trigger[row]))+','+
#                    str(int(ttl_total_count[row]))+','+
#                    str(int(lick_rate[row]))+','+
                    str(int(lap_count[row]))+','+
                    str(int(environment[row])) + '\n')
        big_file.write(new_line)

     

#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

file_names = [os.path.join(directory_path, f)
    for dirpath, dirnames, files in os.walk(directory_path)
    for f in files if f.endswith('.csv')]
file_names.sort(key=natural_key)

#now extract details for each frame:
for filez in file_names:
        print filez
        #check whether there is already a pdf
        if os.path.isfile(filez + '_per_frame.csv'):
            print 'An per_frame file already exists for this file. Delete the old per_frame file to generate a new one.'
        else:
            extract_details_per_frame(filez)