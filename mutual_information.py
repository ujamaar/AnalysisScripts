import numpy # needed for various math tasks
import os # needed to arrange filenames alphabetically
import re # needed to arrange filenames alphabetically

def main():

    directory_path ='/Users/njoshi/Desktop/data_analysis/input_files'

    number_of_shuffles = 100

    #detect all the .csv files in the folder
    file_names = [os.path.join(directory_path, f)
        for dirpath, dirnames, files in os.walk(directory_path)
        for f in files if f.endswith('.csv')]
    file_names.sort(key=natural_key)
    
    
    if (len(file_names) == 2):
        print '----------------------------------------------------------------'
        print 'Cell events file:        ' + file_names[0]
        print 'Reference variable file: ' + file_names[1]               

        cell_events = numpy.loadtxt(file_names[0], dtype='int', comments='#', delimiter=',',skiprows=2)
        #cell_events = cell_events.transpose() # now each row is a cell and each column is a frame
        reference_variable = numpy.loadtxt(file_names[1], dtype='int', comments='#', delimiter=',',skiprows=2)

        print 'Calculating mutual information now:'

        mutual_infomation_test_of_shuffled_cell_events(cell_events,reference_variable,number_of_shuffles)
    else:
        print "Please make sure that there are an appropriate number of files in the folder"

#to make sure that the files are processed in the proper order
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


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


def calculate_mutual_information (cell_events,reference_variable):
    
    total_number_of_cells = cell_events.shape[0]
    total_number_of_frames = cell_events.shape[1]    
    
    if (len(reference_variable) != total_number_of_frames):
        print 'Frame numbers do not match between events file and reference variable file'
        return

    number_of_ref_vars = max(reference_variable) + 1

    prob_Y = numpy.zeros(number_of_ref_vars,dtype='float')

    prob_X0 = numpy.zeros(total_number_of_cells,dtype='float')
    prob_X1 = numpy.zeros(total_number_of_cells,dtype='float')

    prob_X0_and_Y = numpy.zeros((total_number_of_cells,number_of_ref_vars),dtype='float')
    prob_X1_and_Y = numpy.zeros((total_number_of_cells,number_of_ref_vars),dtype='float')

    mutual_information = numpy.zeros(total_number_of_cells,dtype='float')

    unique_ref_vars,frequency_of_each_ref_var = get_unique_elements(reference_variable,return_index=False, return_inverse=False,return_counts=True)
    
    for ref_var in range(0,number_of_ref_vars):
        prob_Y[ref_var] = frequency_of_each_ref_var[ref_var]*1.00/total_number_of_frames
        
        index = 0
        cell_frames_with_current_ref_var = numpy.zeros((total_number_of_cells,frequency_of_each_ref_var[ref_var]),dtype='float')
        for frame in range(0,total_number_of_frames):
            if(reference_variable[frame] == ref_var):
                cell_frames_with_current_ref_var[:,index] = cell_events[:,frame]  #for all cells, pick out only those frames where current ref_var is true
                index = index + 1
        
        for cell in range(0,total_number_of_cells):
            prob_X0_and_Y[cell][ref_var] = (((frequency_of_each_ref_var[ref_var] - numpy.sum(cell_frames_with_current_ref_var[cell,:]))+1.00)/(frequency_of_each_ref_var[ref_var]+2.00)) * prob_Y[ref_var]
            prob_X1_and_Y[cell][ref_var] = ((numpy.sum(cell_frames_with_current_ref_var[cell,:])+1.00)/(frequency_of_each_ref_var[ref_var]+2.00)) * prob_Y[ref_var]
            

    for cell in range(0,total_number_of_cells):

        prob_X0[cell] = (total_number_of_frames*1.00 - numpy.sum(cell_events[cell,:]))/total_number_of_frames
        prob_X1[cell] = (numpy.sum(cell_events[cell,:]) * 1.00)/total_number_of_frames

        cell_mutual_info_X0 = 0.00
        cell_mutual_info_X1 = 0.00
        for ref_var in range(0,number_of_ref_vars):
            cell_mutual_info_X0 += (prob_X0_and_Y[cell][ref_var] * (numpy.log((prob_X0_and_Y[cell][ref_var])/(prob_X0[cell] * prob_Y[ref_var]))))
            cell_mutual_info_X1 += (prob_X1_and_Y[cell][ref_var] * (numpy.log((prob_X1_and_Y[cell][ref_var])/(prob_X1[cell] * prob_Y[ref_var]))))
        mutual_information[cell] = cell_mutual_info_X0 + cell_mutual_info_X1
                

    return mutual_information



#################################################################################

def mutual_infomation_test_of_shuffled_cell_events(cell_events,reference_variable,number_of_shuffles):

    cell_events = cell_events.transpose()
    total_number_of_cells = cell_events.shape[0]    
    total_number_of_frames = cell_events.shape[1]
    print 'Number of cells: %d'%total_number_of_cells
    print 'Number of frames: %d'%total_number_of_frames

    original_mutual_information = calculate_mutual_information(cell_events, reference_variable)    
    
    mutual_information_larger_than_original = numpy.zeros(total_number_of_cells,dtype='int')
    
    cell_events = cell_events.transpose()
    for shuffle in range(0,number_of_shuffles):
        if(shuffle%10==0):
            print 'Shuffle# %d'%shuffle

        shuffled_cell_events = numpy.random.permutation(cell_events)
        shuffled_cell_events = shuffled_cell_events.transpose()

        
#        shuffled_cell_events = numpy.zeros((total_number_of_cells,cell_events.shape[1]),dtype='int')
#        for cell in range(0,total_number_of_cells):
#            shuffled_cell_events[cell,:] = numpy.random.permutation(cell_events[cell,:])

        mutual_information_of_shuffled_events = calculate_mutual_information(shuffled_cell_events, reference_variable)
        
        for cell in range(0,total_number_of_cells):
            if(mutual_information_of_shuffled_events[cell] >= original_mutual_information[cell]):
                mutual_information_larger_than_original[cell] += 1

    p_values_shuffle_test = numpy.zeros(total_number_of_cells,dtype='float')
    
    for cell in range (0,total_number_of_cells):
        p_values_shuffle_test[cell] = float(mutual_information_larger_than_original[cell]) / float(number_of_shuffles)


    #create an output folder for each input file
    output_dir_path = '/Users/njoshi/Desktop/data_analysis/output_files/'
    if output_dir_path:
        if not os.path.isdir(output_dir_path):
            os.makedirs(output_dir_path) 
    numpy.savetxt(output_dir_path + '/mutual_information_per_cell.csv', original_mutual_information , fmt='%1.10f', delimiter=',', newline='\n')
    numpy.savetxt(output_dir_path + '/pvalues_of_mutual_information_per_cell.csv', p_values_shuffle_test , fmt='%1.10f', delimiter=',', newline='\n')
    numpy.savetxt(output_dir_path + '/mutual_information_larger_than_original_%d.csv'%number_of_shuffles, mutual_information_larger_than_original , fmt='%i', delimiter=',', newline='\n')

#################################################################################
#################################################################################
main()







