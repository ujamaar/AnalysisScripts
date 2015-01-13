#http://stackoverflow.com/questions/27578648/customizing-colors-in-matplotlib-heatmap

#import matplotlib.pyplot as plt
#from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import numpy as np
#from matplotlib.backends.backend_pdf import PdfPages
import os
import re

def read_data_and_generate_plots(file_path):
    
    event_data = np.loadtxt(file_path, dtype='int', delimiter=',')

    number_of_frames = event_data.shape[0]      
    number_of_cells = event_data.shape[1]-9

    print 'In this file:'
    print "Number of frames = %d" %number_of_frames
    print "Number of cells  = %d" %number_of_cells

    for cell in range(9,event_data.shape[1]):
        for frame in range(0,number_of_frames):
            if(event_data[frame][cell] > 0):
               event_data[frame][cell] = 0
               
               #insert the event in a new random location
               new_frame_for_this_event = (number_of_frames * np.random.rand()) / 1
               event_data[new_frame_for_this_event][cell] = 1
               
               print 'Event was at frame %d and now it is at %d' %(frame,new_frame_for_this_event)

    np.savetxt(file_path.replace('.csv','_randomly_shuffled_events.csv'), event_data, fmt='%i', delimiter=',', newline='\n')
            


#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

def main():
    #for PC, the format is something like: directory_path ='C:/Users/axel/Desktop/test_data'
    directory_path ='/Users/njoshi/Desktop/events_test'
#    odor_response_time_window = 2000 #time in ms
#    distance_bin_size = 50 #distance bin in mm
#    speed_threshold = 5 #minimum speed in cm/s for seecting evets
#    gaussian_filter_sigma = 1.5
#    #odor_response_distance_window = 500 #in mm
    
    file_names = [os.path.join(directory_path, f)
        for dirpath, dirnames, files in os.walk(directory_path)
        for f in files if f.endswith('.csv')]
    file_names.sort(key=natural_key)
    
    for mouse_data in file_names:
        print 'Analyzing this file: '+ mouse_data
#        if os.path.isfile(mouse_data.replace(".csv","_sorted_place_cells.pdf")):
#            print 'A pdf already exists for this file. Delete the pdf to generate a new one.'
#        else:
#        read_data_and_generate_plots(mouse_data,odor_response_time_window, distance_bin_size,speed_threshold,gaussian_filter_sigma)
        read_data_and_generate_plots(mouse_data)

main()