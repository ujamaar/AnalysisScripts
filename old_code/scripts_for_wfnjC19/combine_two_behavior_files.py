import os
import numpy
import re

#this script is for selecting valid cells from events file and then combining the behavior data with event data

#for PC, the format is something like: directory_path ='C:/Users/axel/Desktop/test_data'
directory_path ='/Users/njoshi/Desktop/events_test'

def combine_behavior_files (behavior_input_file_1, behavior_input_file_2):
    #TTLtotalCount,Time,Valve,LickCount,RewardCount,InitialDropCount,RewardWindow,Distance,TotalDistance,LapCount,Environment
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

    
    behavior_input_1 = numpy.loadtxt(behavior_input_file_1, dtype='int', comments='#', delimiter=',',skiprows=2)
    behavior_input_2 = numpy.loadtxt(behavior_input_file_2, dtype='int', comments='#', delimiter=',',skiprows=2)    

    behavior = numpy.empty((behavior_input_1.shape[0]+behavior_input_2.shape[0],behavior_input_1.shape[1]),dtype='int')

    print "Behavior input file 1 has size: "
    print behavior_input_1.shape
    print "Behavior input file 2 has size: "
    print behavior_input_2.shape
    print "Behavior output file has size: "
    print behavior.shape

    
    for row in range(0, behavior_input_1.shape[0]):
        behavior[row][0] = behavior_input_1[row][0]
        behavior[row][1] = behavior_input_1[row][1]
        behavior[row][2] = behavior_input_1[row][2]
        behavior[row][3] = behavior_input_1[row][3]
        behavior[row][4] = behavior_input_1[row][4]
        behavior[row][5] = behavior_input_1[row][5]        
        behavior[row][6] = behavior_input_1[row][6]
        behavior[row][7] = behavior_input_1[row][7]
        behavior[row][8] = behavior_input_1[row][8]
        behavior[row][9] = behavior_input_1[row][9]
        behavior[row][10] = behavior_input_1[row][10]

    print 'Done adding first file'    
    last_row = behavior_input_1.shape[0]

    for row in range(0,behavior_input_2.shape[0]):

        behavior[last_row + row][0] = behavior_input_2[row][0] + behavior_input_1[last_row-1][0]
        behavior[last_row + row][1] = behavior_input_2[row][1] + behavior_input_1[last_row-1][1]
        behavior[last_row + row][2] = behavior_input_2[row][2]
        behavior[last_row + row][3] = behavior_input_2[row][3] + behavior_input_1[last_row-1][3]
        behavior[last_row + row][4] = behavior_input_2[row][4] + behavior_input_1[last_row-1][4]
        behavior[last_row + row][5] = behavior_input_2[row][5] + behavior_input_1[last_row-1][5]
        behavior[last_row + row][6] = behavior_input_2[row][6]
        behavior[last_row + row][7] = behavior_input_2[row][7]
        behavior[last_row + row][8] = behavior_input_2[row][8] + behavior_input_1[last_row-1][8]
        behavior[last_row + row][9] = behavior_input_2[row][9] + behavior_input_1[last_row-1][9] + 1
        behavior[last_row + row][10] = behavior_input_2[row][10] + 1

    print 'Done adding second file'

    numpy.savetxt(behavior_input_file_1.replace('.csv','_combined_behavior.csv'), behavior, fmt='%i', delimiter=',', newline='\n')
    print 'Done saving output file'

###############################################################################
###############################################################################
###############################################################################


#to make sure that the files are processed in the proper order (not really important here, but just in case)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def main():
    #detect all the .csv files in the folder
    file_names = [os.path.join(directory_path, f)
        for dirpath, dirnames, files in os.walk(directory_path)
        for f in files if f.endswith('.csv')]
    file_names.sort(key=natural_key)

    #now on to the actual analysis:
    if (len(file_names) == 2):
        print 'The two files to be combined are:'
        print 'First file: '+ file_names[0]
        print 'Second file: '+ file_names[1]
        combine_behavior_files(file_names[0],file_names[1])
    else:
        print "Please make sure that there are only two behavior files in the folder for combining"
main()

