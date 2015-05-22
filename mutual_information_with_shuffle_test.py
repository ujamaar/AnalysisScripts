import numpy # needed for various math tasks
import os # needed to find files
import re # needed to arrange filenames alphabetically

#set number_of_shuffles = 0 if you only need to calculate mutual information, without doing any shuffle test

def main():

    ################# sample file paths for windows  ##################
    input_directory_path = 'C:/Users/axel/Desktop/data_analysis/input_files'
    #input_directory_path = '//losonczy-server/walter/Virtual_Odor/imaging_data/'

    ################# sample file paths for mac  ##################    
    #input_directory_path ='/Volumes/walter/Virtual_Odor/imaging_data'
    #input_directory_path  = '/Users/njoshi/Desktop/data_analysis/input_files'

    number_of_shuffles = 10000


    replace_previous_versions_of_output_files = False
    
    #detect all the mi_input_cell_events.csv files in the folder
    cell_events_file_names = []
    for dirpath, dirnames, files in os.walk(input_directory_path):
        for cell_events_file in files:
            if cell_events_file.endswith('mi_cell_events.csv'):
                if(replace_previous_versions_of_output_files == True):
                    cell_events_file_names.append(os.path.join(dirpath, cell_events_file))
                else:                  
                    file_has_already_been_analyzed = False
                    for mutual_info_file in files:
                        if mutual_info_file.endswith('mutual_info.csv'):
                            file_has_already_been_analyzed = True
                            print 'Mutual information has already been calculated: ' + cell_events_file
                            print 'Delete this mutual information file to rerun the test: ' + mutual_info_file

                    
                    if(file_has_already_been_analyzed == False):      
                        cell_events_file_names.append(os.path.join(dirpath, cell_events_file))
    # sort the file names to analyze them in a 'natural' alphabetical order
    cell_events_file_names.sort(key=natural_key)    
    print 'Here are all of the cell event files for which mutual information will be calculated:'
    print cell_events_file_names



    # now look for imaging data for each behavior file and combine all the data into one output file    
    for cell_events_file in cell_events_file_names:
        print '----------------------------------------------------------------'
        print '----------------------------------------------------------------'
        print 'Analysing this cell events file: '+ cell_events_file
        
        # now load the events, valid_cells and missing_frames files for the given behavior file
        # first extract the mouse ID and date from behavior file, to find the right imaging files
        mouse_ID_first_letter = 0
        file_length = len(cell_events_file)
        for name_letter in range (1,file_length):
            if(cell_events_file[file_length - name_letter] == 'w' or cell_events_file[file_length - name_letter] == 'W'):
                mouse_ID_first_letter = file_length - name_letter
                break
        mouse_ID_and_date = cell_events_file[mouse_ID_first_letter:(mouse_ID_first_letter+18)] #mouse ID and date are written using 18 characters
        print 'Mouse ID is: %s'%mouse_ID_and_date

        reference_variable_file_directory_path = ''
        for name_letter in range (1,file_length):
            if(cell_events_file[file_length - name_letter] == '/'):
                reference_variable_file_directory_path = cell_events_file[0:(file_length - name_letter)]
                break

        print 'Checking this location for reference variable files:  ' + reference_variable_file_directory_path

        mutual_info_reference_variable_files = [os.path.join(reference_variable_file_directory_path, f)
            for dirpath, dirnames, files in os.walk(reference_variable_file_directory_path)
            for f in files if f.endswith('ref_var.csv')]
        mutual_info_reference_variable_files.sort(key=natural_key)

        if (len(mutual_info_reference_variable_files) == 0):
            print "To calculate mutul information for cell events, please make sure that there is at least one reference variable file in the folder."
        else:
            print 'Calculating mutual information now for %d reference variables:'%(len(mutual_info_reference_variable_files))
            mutual_infomation_test_of_shuffled_cell_events(cell_events_file,mutual_info_reference_variable_files,number_of_shuffles)

    #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><#

#################################################################################

def mutual_infomation_test_of_shuffled_cell_events(cell_events_file,all_mutual_info_reference_variable_files,number_of_shuffles):
    
    cell_events = numpy.loadtxt(cell_events_file, dtype='int', comments='#', delimiter=',',skiprows=0)

    total_number_of_frames = cell_events.shape[0]
    total_number_of_cells = cell_events.shape[1]    
    print 'Number of cells: %d'%total_number_of_cells
    print 'Number of frames: %d'%total_number_of_frames

    #read all the reference variables into a tuple
    reference_variables = [list(numpy.loadtxt(all_mutual_info_reference_variable_files[ref_var], dtype='int', comments='#', delimiter=',',skiprows=0)) for ref_var in xrange(len(all_mutual_info_reference_variable_files))]
    number_of_reference_variables = len(reference_variables)
    print 'There are %d reference variables'%number_of_reference_variables

    #calculate mutual information
    original_mutual_information_lists = [list(calculate_mutual_information(cell_events, reference_variables[ref_var])) for ref_var in xrange(number_of_reference_variables)]
    for ref_var in xrange(number_of_reference_variables):
        numpy.savetxt(all_mutual_info_reference_variable_files[ref_var].replace('ref_var.csv','mutual_info.csv'), original_mutual_information_lists[ref_var], fmt='%1.10f', delimiter=',', newline='\n')
    print 'Calculated and saved mutual information.'

    if(number_of_shuffles > 0):
        mutual_information_larger_than_original_lists = [list(numpy.zeros(total_number_of_cells,dtype='int')) for ref_var in xrange(number_of_reference_variables)]    
        
        #now shuffle cell events and calculate mutual information for each shuffle:
        print_interval = 50
        #print_interval = max(5,number_of_shuffles/10)
        for shuffle in range(0,number_of_shuffles):
            if((shuffle+1)%print_interval==0):
                print 'Shuffle# %d  of  %d'%(shuffle+1,number_of_shuffles)
            #shuffled_cell_events = cell_events[numpy.random.permutation(total_number_of_frames),:]  #alternative method of shuffling cel events
            numpy.random.shuffle(cell_events)
    
            shuffled_events_mutual_information_lists = [list(calculate_mutual_information(cell_events, reference_variables[ref_var])) for ref_var in xrange(number_of_reference_variables)]        
    #        mutual_information_of_shuffled_events = calculate_mutual_information(cell_events, reference_variables[ref_var]) 
    
            for ref_var in xrange(number_of_reference_variables):        
                for cell in xrange(total_number_of_cells):
                    if(shuffled_events_mutual_information_lists[ref_var][cell] >= original_mutual_information_lists[ref_var][cell]):
                        mutual_information_larger_than_original_lists[ref_var][cell] += 1
        
        p_values_from_shuffle_test_lists = [list(numpy.zeros(total_number_of_cells,dtype='float')) for ref_var in xrange(number_of_reference_variables)]    
        for ref_var in xrange(number_of_reference_variables):
            for cell in xrange(total_number_of_cells):
                p_values_from_shuffle_test_lists[ref_var][cell] = float(mutual_information_larger_than_original_lists[ref_var][cell]) / float(number_of_shuffles)
            
            numpy.savetxt(all_mutual_info_reference_variable_files[ref_var].replace('ref_var.csv','%ds_pvalues.csv'%number_of_shuffles), p_values_from_shuffle_test_lists[ref_var], fmt='%1.10f', delimiter=',', newline='\n')


#################################################################################


def calculate_mutual_information (cell_events,reference_variable):
    
    total_number_of_cells = cell_events.shape[1]
    total_number_of_frames = cell_events.shape[0]
    number_of_ref_var_values = max(reference_variable) + 1 

    
    if (len(reference_variable) != total_number_of_frames):
        print 'Frame numbers do not match between events file and reference variable file'
        return

    prob_Y             = numpy.zeros(number_of_ref_var_values,dtype='float')
    prob_X0_and_Y      = numpy.zeros((total_number_of_cells,number_of_ref_var_values),dtype='float')
    prob_X1_and_Y      = numpy.zeros((total_number_of_cells,number_of_ref_var_values),dtype='float')
    mutual_information = numpy.zeros(total_number_of_cells,dtype='float')

    unique_ref_vars,frequency_of_each_reference_variable = get_unique_elements(reference_variable,return_index=False, return_inverse=False,return_counts=True)
  
    for ref_var_value in range(0,number_of_ref_var_values):        
        prob_Y[ref_var_value] = frequency_of_each_reference_variable[ref_var_value]*1.00/total_number_of_frames
        
        ref_var_indices = [i for i, x in enumerate(reference_variable) if x == ref_var_value]
        sum_of_cell_events_with_current_ref_var = numpy.sum(numpy.take(cell_events, ref_var_indices,axis=0),axis=0)

        probability_of_Y = prob_Y[ref_var_value]
        frequency_of_this_ref_var = frequency_of_each_reference_variable[ref_var_value]        
        for cell in range(0,total_number_of_cells): 
            prob_X0_and_Y[cell][ref_var_value] = (((frequency_of_this_ref_var - sum_of_cell_events_with_current_ref_var[cell])+1.00)/(frequency_of_this_ref_var+2.00)) * probability_of_Y
            prob_X1_and_Y[cell][ref_var_value] = ((sum_of_cell_events_with_current_ref_var[cell]+1.00)/(frequency_of_this_ref_var+2.00)) * probability_of_Y

    sum_of_cell_events_for_all_cells = numpy.sum(cell_events,axis=0) 
    for cell in range(0,total_number_of_cells):

        prob_X0 = (total_number_of_frames*1.00 - sum_of_cell_events_for_all_cells[cell])/total_number_of_frames
        prob_X1 = (sum_of_cell_events_for_all_cells[cell] * 1.00)/total_number_of_frames

        cell_mutual_info_X0 = 0.00
        cell_mutual_info_X1 = 0.00
        for ref_var_value in range(0,number_of_ref_var_values):
            cell_mutual_info_X0 += (prob_X0_and_Y[cell][ref_var_value] * (numpy.log((prob_X0_and_Y[cell][ref_var_value])/(prob_X0 * prob_Y[ref_var_value]))))
            cell_mutual_info_X1 += (prob_X1_and_Y[cell][ref_var_value] * (numpy.log((prob_X1_and_Y[cell][ref_var_value])/(prob_X1 * prob_Y[ref_var_value]))))
        mutual_information[cell] = cell_mutual_info_X0 + cell_mutual_info_X1

    return mutual_information


#################################################################################


#to make sure that the files are processed in the proper order
def natural_key(string_):
    """Source: See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


#################################################################################


##this function was copied from the numpy source file as is##
##the source is here: https://github.com/numpy/numpy/blob/v1.9.1/numpy/lib/arraysetops.py#L96
def get_unique_elements(ar, return_index=False, return_inverse=False, return_counts=False):

    ar = numpy.asanyarray(ar).flatten()

    optional_indices = return_index or return_inverse
    optional_returns = optional_indices or return_counts

    if ar.size == 0:
        if not optional_returns:
            ret = ar
        else:
            ret = (ar,)
            if return_index:
                ret += (numpy.empty(0, numpy.bool),)
            if return_inverse:
                ret += (numpy.empty(0, numpy.bool),)
            if return_counts:
                ret += (numpy.empty(0, numpy.intp),)
        return ret

    if optional_indices:
        perm = ar.argsort(kind='mergesort' if return_index else 'quicksort')
        aux = ar[perm]
    else:
        ar.sort()
        aux = ar
    flag = numpy.concatenate(([True], aux[1:] != aux[:-1]))

    if not optional_returns:
        ret = aux[flag]
    else:
        ret = (aux[flag],)
        if return_index:
            ret += (perm[flag],)
        if return_inverse:
            iflag = numpy.cumsum(flag) - 1
            iperm = perm.argsort()
            ret += (numpy.take(iflag, iperm),)
        if return_counts:
            idx = numpy.concatenate(numpy.nonzero(flag) + ([ar.size],))
            ret += (numpy.diff(idx),)
    return ret
#################################################################################


#################################################################################
main()