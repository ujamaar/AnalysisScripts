import shutil
import os

input_directory_path = '/Volumes/walter/Virtual_Odor/imaging_data/wfnjC23'
output_directory_path = '/Users/njoshi/Desktop/data_analysis/copy_of_wfnjC_files'

#input_directory_path = '/Users/njoshi/Desktop/data_analysis/input_files'
#output_directory_path = '/Users/njoshi/Desktop/data_analysis/copy_of_files'



for dirpath, dirnames, files in os.walk(input_directory_path):
    for mi_file in files:
        if (mi_file.endswith('mi_cell_events.csv') or mi_file.endswith('ref_var.csv')):
            mouse_ID = mi_file[0:7]
            mouse_ID_and_date = mi_file[0:18]         

            #create create a folder, if it is not already there 
            mouse_day_file_directory_path = output_directory_path + '/' + mouse_ID  + '/' + mouse_ID_and_date

            if mouse_day_file_directory_path:
                if not os.path.isdir(mouse_day_file_directory_path):
                    os.makedirs(mouse_day_file_directory_path)

            shutil.copy2(dirpath + '/' + mi_file, mouse_day_file_directory_path)
