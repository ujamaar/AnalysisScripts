import os
import numpy
import re

#this script is for adjust the frame index number for cases where two or more imaging files are combined

#for PC, the format is something like: directory_path ='C:/Users/axel/Desktop/test_data'
directory_path ='/Users/njoshi/Desktop/events_test'

def extract_details_per_frame (dropped_frames):

    missing_frames = numpy.loadtxt(dropped_frames, dtype='int', comments='#', delimiter=',')
    print "Number of dropped frames: %d"%missing_frames.size
    
    adjustment_amount= 0
    print "Number that frame indices need to be adjusted by: %d"%adjustment_amount   
    
    for n in range(0,len(missing_frames)):
        missing_frames[n] = missing_frames[n] + adjustment_amount
    
    numpy.savetxt(dropped_frames.replace('.csv','_adjusted.csv'), missing_frames, fmt='%d', delimiter=',', newline='\n')    
    
#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

file_names = [os.path.join(directory_path, f)
    for dirpath, dirnames, files in os.walk(directory_path)
    for f in files if f.endswith('.csv')]
file_names.sort(key=natural_key)

# if there are missing frames, run this statement
if (len(file_names) == 1):
    print "Looks like the missing frames need some adjustment"
    print 'Missing frames are saved in this file: '+ file_names[0]
    extract_details_per_frame(file_names[0])
else:
    print "Please make sure that there are an appropriate number of files in the folder"