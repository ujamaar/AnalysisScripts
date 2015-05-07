import numpy # needed for various math tasks
import os # needed to find files



def main():

#    data_files_directory_path ='/Users/njoshi/Desktop/data_analysis/wfnjC8'
    data_files_directory_path ='/Users/njoshi/Desktop/data_analysis/input_files'

    file_names = [os.path.join(data_files_directory_path, f)
        for dirpath, dirnames, files in os.walk(data_files_directory_path)
        for f in files if f.endswith('behavior.csv')]

    
    # now look for imaging data for each behavior file and combine all the data into one output file    
    for behavior_file in file_names:
        print '----------------------------------------------------------------'
        print '----------------------------------------------------------------'
        print 'Analysing this behavior file: '+ behavior_file
        
        raw_behavior = numpy.loadtxt(behavior_file, dtype='int', comments='#', delimiter=',',skiprows=2)
        
        behavior = raw_behavior


#        behavior = numpy.empty((raw_behavior.shape[0],11),dtype='int') 
#        
#
#        behavior[:,0] = raw_behavior[:,13]
#        behavior[:,1] = raw_behavior[:,0]
#        behavior[:,2] = 0   #raw_behavior[:,1]
#        behavior[:,3] = raw_behavior[:,3]            
#        behavior[:,4] = raw_behavior[:,5]
#        behavior[:,5] = raw_behavior[:,10]
#        behavior[:,6] = raw_behavior[:,8]
#        behavior[:,7] = raw_behavior[:,6]
#        behavior[:,8] = raw_behavior[:,7]            
#        behavior[:,9] = raw_behavior[:,15]
#
#        if(raw_behavior.shape[1] == 17):
#            behavior[:,10] = raw_behavior[:,16]
#        else:
#            behavior[:,10] = 1


        numpy.savetxt(behavior_file.replace('behavior.csv','converted_behavior.csv'), behavior, fmt='%i', delimiter=',', newline='\n')

main()