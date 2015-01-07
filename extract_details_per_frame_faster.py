import os
import numpy
import re

#this script is for extracting columns of interest and saving them to a new file
#some inspiration: http://stackoverflow.com/questions/18458734/python-plot-list-of-tuples

#directory_path ='C:/Users/axel/Desktop/test_data'
#directory_path ='//losonczy-server/walter/Virtual_Odor/behavior_data/wfnjC8'

#directory path format for mac computers:
directory_path ='/Users/njoshi/Desktop/events_test'
#directory_path ='/Volumes/walter/Virtual_Odor/behavior_data/wfnjC8'

def extract_details_per_frame (complete_file):
    
    #fast_output_array = numpy.loadtxt(complete_file, dtype='int', comments='#', delimiter=',', converters=None, skiprows=2, usecols=(0,1,3,5,6,12,15), unpack=False, ndmin=0) 
    
    #simply read the relevant columns:
    #fast_output_array = numpy.loadtxt(complete_file, dtype='int', comments='#', delimiter=',', skiprows=2, usecols=(0,1,3,5,6,12,15))
    #write the generated array into an output file:
    #numpy.savetxt(complete_file + '_test_shorter_extraction.csv', fast_output_array, fmt='%i', delimiter=',', newline='\n', header='sri_ganeshaya_namah', footer='iti_shree', comments='#shanti_shanti_shanti#')
    

    input_array = numpy.loadtxt(complete_file, dtype='int', comments='#', delimiter=',', skiprows=2)
    
    output_array = numpy.empty((input_array[len(input_array) - 1][13],8))
    i = -1
    
    for row in range(0, len(input_array)):
        #save data only if there's a new frame in the current data reading
        if(input_array[row][12] > 0):
            i = i + 1
            output_array[i][0] = input_array[row][12]   #frame count
            output_array[i][1] = input_array[row][0]    #time
            output_array[i][2] = input_array[row][1]    #odor
            output_array[i][3] = input_array[row][3]    #lick count
            output_array[i][4] = input_array[row][5]    #reward count
            output_array[i][5] = input_array[row][6]    #distance
            output_array[i][6] = input_array[row][15]   #lap count
            if(input_array.shape[1]>=17):               #environment
                output_array[i][7] = input_array[row][16]   
            else:
                output_array[i][7] = 1
            
            #add a line for the speed here
            #output_array[i][8] = current_speed
       
            # alternative method, but allegedly less efficient: output_array = numpy.vstack([output_array,new_row])
    
    #now save the array as a csv file in the same location as the input file
    numpy.savetxt(complete_file.replace('.csv','_per_frame.csv'), output_array, fmt='%i', delimiter=',', newline='\n')


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
        print 'A per_frame file already exists for this file. Delete the old per_frame file to generate a new one.'
    else:
        print 'Extracting data from behavior file:'
        print filez
        extract_details_per_frame(filez)