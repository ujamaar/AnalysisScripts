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
directory_path ='/Users/njoshi/Documents/nwp_test_data'
#directory_path ='/Volumes/walter/Virtual_Odor/behavior_data/wfnjC8'

def combine_files(file1,file2, output_filename):
    
    print "Combining two files in this sequence:"
    print file1
    print file2
    
    data = [pylab.loadtxt(file1, delimiter=',',skiprows=2)]
    datalist1 = data[0]
    
    data = [pylab.loadtxt(file2, delimiter=',',skiprows=2)]
    datalist2 = data[0]    
    
    time = []
    valves = []
    licks = []
    lick_count = []
    rewards = []
    reward_count = []	
    distance = []
    total_distance = []
    reward_availability = []
    initial_drop = []
    initial_drop_count = []
    imaging_trigger = []
    ttl_pulse = []
    ttl_total_count = []
    lick_rate = []
    lap_count = []
    environment = []

    #read data points from the tuple into lists, which are easier to work with
    for row in range(0,len(datalist1)):
        time.append(datalist1[row][0])
        valves.append(datalist1[row][1])    
        licks.append(datalist1[row][2])
        lick_count.append(datalist1[row][3])
        rewards.append(datalist1[row][4])
        reward_count.append(datalist1[row][5])
        distance.append(datalist1[row][6])
        total_distance.append(datalist1[row][7])
        reward_availability.append(datalist1[row][8])
        initial_drop.append(datalist1[row][9])
        initial_drop_count.append(datalist1[row][10])
        imaging_trigger.append(datalist1[row][11])
        ttl_pulse.append(datalist1[row][12])
        ttl_total_count.append(datalist1[row][13])
        lick_rate.append(datalist1[row][14])
        lap_count.append(int(datalist1[row][15]))
        
        if(len(datalist1[row]) == 17):
            environment.append(int(datalist1[row][16]))
        else:
            environment.append(1)

    ##do some simple arithmetic here to make all of the values in file2 continuous with values in file1
    ## then it's a simple matter of appending the values:
    for row in range(0,len(datalist2)):
        time.append(time[len(datalist1)-1] + datalist2[row][0])
        valves.append(datalist2[row][1])    
        licks.append(datalist2[row][2])
        lick_count.append(lick_count[len(datalist1)-1] + datalist2[row][3])
        rewards.append(datalist2[row][4])
        reward_count.append(reward_count[len(datalist1)-1] + datalist2[row][5])
        distance.append(datalist2[row][6])
        total_distance.append(total_distance[len(datalist1)-1] + datalist2[row][7])
        reward_availability.append(datalist2[row][8])
        initial_drop.append(datalist2[row][9])
        initial_drop_count.append(initial_drop_count[len(datalist1)-1] + datalist2[row][10])
        imaging_trigger.append(datalist2[row][11])

        ttl_total_count.append(ttl_total_count[len(datalist1)-1] + datalist2[row][13])
        lick_rate.append(datalist2[row][14])
        lap_count.append(lap_count[len(datalist1)-1] + int(datalist2[row][15]) +1)
        
        if(len(datalist2[row]) == 17):
            environment.append(environment[len(datalist1)-1] + int(datalist2[row][16]))
        else:
            environment.append(0)
        
        
        if(datalist2[row][12] > 0):
            ttl_pulse.append(ttl_total_count[len(datalist1)-1] + datalist2[row][12])
        else:
            ttl_pulse.append(2)

    ##now just save all the lists together in a .csv file
    
    
    
    
    big_file = open(output_filename, "a+")
    
    print "The combined file is:"
    print output_filename
    
    for row in range(0,len(time)):
        new_line = (str(int(time[row]))+','+
                    str(int(valves[row]))+','+
                    str(int(licks[row]))+','+
                    str(int(lick_count[row]))+','+
                    str(int(rewards[row]))+','+
                    str(int(reward_count[row]))+','+
                    str(int(distance[row]))+','+
                    str(int(total_distance[row]))+','+
                    str(int(reward_availability[row]))+','+
                    str(int(initial_drop[row]))+','+
                    str(int(initial_drop_count[row]))+','+
                    str(int(imaging_trigger[row]))+','+
                    str(int(ttl_pulse[row]))+','+
                    str(int(ttl_total_count[row]))+','+
                    str(int(lick_rate[row]))+','+
                    str(int(lap_count[row]))+','+
                    str(int(environment[row])) + '\n')
        big_file.write(new_line)

#source: http://stackoverflow.com/questions/18715688/find-common-substring-between-two-strings    
def longestSubstringFinder(string1, string2):
    answer = ""
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = ""
        for j in range(len2):
            if (i + j < len1 and string1[i + j] == string2[j]):
                match += string2[j]
            else:
                if (len(match) > len(answer)): answer = match
                match = ""
    return answer + '0000_combined_file.csv'
     

#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

file_names = [os.path.join(directory_path, f)
    for dirpath, dirnames, files in os.walk(directory_path)
    for f in files if f.endswith('.csv')]
file_names.sort(key=natural_key)

output_file = longestSubstringFinder(file_names[0],file_names[1])

#now combine all files in the folder
combine_files(file_names[0],file_names[1], output_file)


