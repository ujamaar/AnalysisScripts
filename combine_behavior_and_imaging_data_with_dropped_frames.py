import os
import numpy
#from pylab import *
import matplotlib.pyplot as plt
import re

#this script is for extracting columns of interest and saving them to a new file
#some inspiration: http://stackoverflow.com/questions/18458734/python-plot-list-of-tuples

#for PC: directory_path ='C:/Users/axel/Desktop/test_data'
directory_path ='/Users/njoshi/Desktop/test_data'

def extract_details_per_frame (behavior,images,dropped_frames):
    
    behavior_data = numpy.loadtxt(behavior, dtype='int', comments='#', delimiter=',')
    print "Behavior array size is: "
    print behavior_data.shape
    
    imaging_data = numpy.loadtxt(images, dtype='float', comments='#', delimiter=',')
    print "Imaging array size is: "
    print imaging_data.shape

    missing_frames = numpy.loadtxt(dropped_frames, dtype='int', comments='#', delimiter=',')
    print "Missing frame array size is: "
    print missing_frames.size

    
    output_file = numpy.empty((behavior_data.shape[0],behavior_data.shape[1]+imaging_data.shape[1]))    
    print "Output array size is: "
    print output_file.shape
    
    adjust_for_missing_frames = 0
    
    for row in range(0, behavior_data.shape[0]):
        #check if the row is missing from the imaging data:
        if(row + 1 in missing_frames):
            adjust_for_missing_frames = adjust_for_missing_frames + 1
            for column in range(0,output_file.shape[1]):
                if (column < behavior_data.shape[1]):
                    output_file[row][column] = behavior_data[row][column]
                else:
                    output_file[row][column] = numpy.nan
        #business is as usual if frames are not missing:
        else:
            for column in range(0,output_file.shape[1]):
                if (column < behavior_data.shape[1]):
                    output_file[row][column] = behavior_data[row][column]
                else:
                    output_file[row][column] = imaging_data[row - adjust_for_missing_frames][column-behavior_data.shape[1]]
       
    
    #now save the array as a csv file in the same location as the input file
    numpy.savetxt(behavior + '_combined_behavior_and_imaging.csv', output_file, fmt='%.5f', delimiter=',', newline='\n')
    
    #generate a sample plot of distance vs events for cell in column#306
    print "now plotting a sample graph:"
    x = output_file[:,5]
    y = output_file[:,308]
    
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    
    ax.plot(x,y)
    plt.xlabel("Distance")
    plt.ylabel("event")
    plt.xlim(0,4500)
    plt.show()
    
#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

file_names = [os.path.join(directory_path, f)
    for dirpath, dirnames, files in os.walk(directory_path)
    for f in files if f.endswith('.csv')]
file_names.sort(key=natural_key)

extract_details_per_frame(file_names[0],file_names[1],file_names[2])