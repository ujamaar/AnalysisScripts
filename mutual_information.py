import numpy # needed for various math tasks
import math
import os # needed to arrange filenames alphabetically
import re # needed to arrange filenames alphabetically

def main():

    directory_path ='/Users/njoshi/Desktop/data_analysis/input_files'

    #detect all the .csv files in the folder
    file_names = [os.path.join(directory_path, f)
        for dirpath, dirnames, files in os.walk(directory_path)
        for f in files if f.endswith('.csv')]
    file_names.sort(key=natural_key)
    
    
    if (len(file_names) == 2):
        print '----------------------------------------------------------------'
        print '----------------------------------------------------------------'
        print 'Cell events file: '+ file_names[0]
        print 'Reference variable file: '+ file_names[1]               
        calculateMutualInformation(file_names[0],file_names[1])
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



def calculateMutualInformation (cell_events_file,reference_variable_file):

    cell_events = numpy.loadtxt(cell_events_file, dtype='int', comments='#', delimiter=',',skiprows=2)
    cell_events = cell_events.transpose() # now each row is a cell and each column is a frame
    reference_variable = numpy.loadtxt(reference_variable_file, dtype='int', comments='#', delimiter=',',skiprows=2)

    total_number_of_cells = cell_events.shape[0]
    total_number_of_frames = cell_events.shape[1]    
    print 'Number of cells: %d'%total_number_of_cells
    print 'Number of frames: %d'%total_number_of_frames
    
    #cell_mutual_information = numpy.zeros(total_number_of_cells,dtype='float')

    if (len(reference_variable) != total_number_of_frames):
        print 'Frame numbers do not match between events file and reference variable file'
        return



    print 'Calculating mutual information now:'

    min_ref_var = min(reference_variable)
    reference_variable_rounded = [numpy.round(ref_var-min_ref_var) for ref_var in reference_variable]
    number_of_ref_vars = max(reference_variable_rounded) + 1

    prob_Y = numpy.zeros(number_of_ref_vars,dtype='float')

    prob_X0 = numpy.zeros(total_number_of_cells,dtype='float')
    prob_X1 = numpy.zeros(total_number_of_cells,dtype='float')

    prob_X0_and_Y = numpy.zeros((total_number_of_cells,number_of_ref_vars),dtype='float')
    prob_X1_and_Y = numpy.zeros((total_number_of_cells,number_of_ref_vars),dtype='float')

    mutual_information = numpy.zeros(total_number_of_cells,dtype='float')

    unique_ref_vars,frequency_of_each_ref_var = get_unique_elements(reference_variable_rounded,return_index=False, return_inverse=False,return_counts=True)
    
    for ref_var in range(0,number_of_ref_vars):
        prob_Y[ref_var] = frequency_of_each_ref_var[ref_var]*1.00/total_number_of_frames
        
        index = 0
        cell_frames_with_current_ref_var = numpy.zeros((total_number_of_cells,frequency_of_each_ref_var[ref_var]),dtype='float')
        for frame in range(0,total_number_of_frames):
            if(reference_variable_rounded[frame] == ref_var):
                cell_frames_with_current_ref_var[:,index] = cell_events[:,frame]  #for all cells, pick out only those frames where current ref_var is true
                index = index + 1
        
        for cell in range(0,total_number_of_cells):
            prob_X0_and_Y[cell][ref_var] = (((frequency_of_each_ref_var[ref_var] - math.fsum(cell_frames_with_current_ref_var[cell,:]))+1.00)/(frequency_of_each_ref_var[ref_var]+2.00)) * prob_Y[ref_var]
            prob_X1_and_Y[cell][ref_var] = ((math.fsum(cell_frames_with_current_ref_var[cell,:])+1.00)/(frequency_of_each_ref_var[ref_var]+2.00)) * prob_Y[ref_var]
            

    for cell in range(0,total_number_of_cells):

        prob_X0[cell] = (total_number_of_frames*1.00 - math.fsum(cell_events[cell,:]))/total_number_of_frames
        prob_X1[cell] = (math.fsum(cell_events[cell,:]) * 1.00)/total_number_of_frames

        cell_mutual_info_X0 = 0.00
        cell_mutual_info_X1 = 0.00
        for ref_var in range(0,number_of_ref_vars):
            cell_mutual_info_X0 = cell_mutual_info_X0 + (prob_X0_and_Y[cell][ref_var] * (math.log((prob_X0_and_Y[cell][ref_var])/(prob_X0[cell] * prob_Y[ref_var]))))
            cell_mutual_info_X1 = cell_mutual_info_X1 + (prob_X1_and_Y[cell][ref_var] * (math.log((prob_X1_and_Y[cell][ref_var])/(prob_X1[cell] * prob_Y[ref_var]))))
        mutual_information[cell] = cell_mutual_info_X0 + cell_mutual_info_X1
                

    #create an output folder for each input file
    output_dir_path = '/Users/njoshi/Desktop/data_analysis/output_files/'
    if output_dir_path:
        if not os.path.isdir(output_dir_path):
            os.makedirs(output_dir_path) 
    numpy.savetxt(output_dir_path + '/mutual_information_per_cell.csv', mutual_information , fmt='%1.10f', delimiter=',', newline='\n')
#################################################################################
main()