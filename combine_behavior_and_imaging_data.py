import os
import numpy
import matplotlib.pyplot as plt
import re

#this script is for extracting columns of interest and saving them to a new file
#some inspiration: http://stackoverflow.com/questions/18458734/python-plot-list-of-tuples

#directory_path ='C:/Users/axel/Desktop/test_data'
#directory_path ='//losonczy-server/walter/Virtual_Odor/behavior_data/wfnjC8'

#directory path format for mac computers:
directory_path ='/Users/njoshi/Desktop/test_data'
#directory_path ='/Volumes/walter/Virtual_Odor/behavior_data/wfnjC8'

def extract_details_per_frame (behavior,images):

    behavior_data = numpy.loadtxt(behavior, dtype='int', comments='#', delimiter=',')
    imaging_data = numpy.loadtxt(images, dtype='float', comments='float', delimiter=',')
    
    print behavior_data.shape
    print imaging_data.shape
    
    output_file = numpy.empty((behavior_data.shape[0],behavior_data.shape[1]+imaging_data.shape[1]))
    
    print output_file.shape
    
    for row in range(0, behavior_data.shape[0]):
        for column in range(0,output_file.shape[1]):
            if (column < behavior_data.shape[1]):
                output_file[row][column] = behavior_data[row][column]
            else:
                output_file[row][column] = imaging_data[row][column-behavior_data.shape[1]]
       
    
    #now save the array as a csv file in the same location as the input file
    numpy.savetxt(behavior + '_combined_behavior_and_imaging.csv', output_file, fmt='%.5f', delimiter=',', newline='\n')
    
    #generate a sample plot of distance vs events for cell in column#306
    x = output_file[:,5]
    y = output_file[:,306]
    
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    
    ax.plot(x,y)
    plt.xlabel("Distance")
    plt.ylabel("event")
    plt.xlim(0,4500)
    plt.show()
    
#    for  in output_file:
#        pylab.plot( data[:,0], data[:,5], label=label )
#
#    pylab.legend()
#    pylab.title("test plot")
#    pylab.xlabel("Imaging Frame")
#    pylab.ylabel("Distance")


#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

file_names = [os.path.join(directory_path, f)
    for dirpath, dirnames, files in os.walk(directory_path)
    for f in files if f.endswith('.csv')]
file_names.sort(key=natural_key)

extract_details_per_frame(file_names[0],file_names[1])