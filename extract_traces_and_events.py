import os
import numpy
import re

#this script is for combining behavior and imaging data
#the column labels are:
#Frames,Time,Odor,Licks,Rewards,Distance,Laps,ImagingTimeInSeconds,(traces of many many cells), (events of those cells)


#for PC, the format is something like: directory_path ='C:/Users/axel/Desktop/test_data'
directory_path ='/Users/njoshi/Desktop/test_data'

def extract_details_per_frame (imaging_file):
    
    imaging_data = numpy.loadtxt(imaging_file, comments='#', delimiter=',')
    print "Input array size is: "
    print imaging_data.shape
        
    traces = numpy.empty((imaging_data.shape[0],(imaging_data.shape[1] + 1) / 2))    
    print "Traces array size is: "
    print traces.shape

    events = numpy.empty((traces.shape))    
    print "Events array size is: "
    print events.shape
    
    for row in range(0, imaging_data.shape[0]):
        traces[row][0] = imaging_data[row][0]
        events[row][0] = imaging_data[row][0]
        
        for column in range(1,traces.shape[1]):
            traces[row][column] = imaging_data[row][column]
            events[row][column] = imaging_data[row][column + traces.shape[1] - 1]
            
           
    #now save the array as a csv file in the same location as the input file
    numpy.savetxt(directory_path + '/traces_extracted.csv', traces, fmt='%.2f', delimiter=',', newline='\n')
    numpy.savetxt(directory_path + '/events_extracted.csv', events, fmt='%.2f', delimiter=',', newline='\n')    

file_names = [os.path.join(directory_path, f)
    for dirpath, dirnames, files in os.walk(directory_path)
    for f in files if f.endswith('.csv')]

if(len(file_names) == 1):
    print "Separating traces and events for all cells in this file:"
    print file_names[0]
    extract_details_per_frame(file_names[0])
else:
    print "Please make sure that there is one (and only one) imaging file in the given folder"
