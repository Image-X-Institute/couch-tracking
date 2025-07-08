# Edit the couch tracking trace where the 6DoF robots were operating too
# early, to not have identical values - hypothesise that identical values
# are read by the robot software as the same position and skipped.
# In addition : centers all the traces around zero

import numpy as np
import os
import glob

# Folder with input .txt files
input_folder = r"C:\Users\imagex_labl\Documents\GitHub\1D-couch-applications\Elisa\Experiments\Motion Traces"
# Output folder
output_folder = r"C:\Users\imagex_labl\Documents\GitHub\1D-couch-applications\Elisa\Experiments\No_5_final\centered_traces"  
os.makedirs(output_folder, exist_ok=True)  # Create if it doesn't exist

file_pattern = os.path.join(input_folder, '*.txt') 
tol = 1e-2  # Tolerance for similarity

# Browse all files
for file_path in glob.glob(file_pattern):
    filename = os.path.basename(file_path)

    # Load data
    data = np.loadtxt(file_path)
      
    # Extract time and motion to be updated
    time = data[:, 0]
    motion = data[:, 2]

    # Modify SI motion if consecutive values are similar
    for i in range(1, len(motion)):
        if abs(motion[i] - motion[i - 1]) < tol:
            motion[i] += 0.1

    # Reconstruct and save new data
    new_data = np.column_stack((data[:, 0:2], motion, data[:, 3:7]))

    # Center all columns EXCEPT time (column 0)
    mean_values = new_data[:, 1:].mean(axis=0)
    new_data[:, 1:] -= mean_values

    output_file = os.path.join(output_folder, filename.replace('.txt', '_UPDATED.txt'))
    np.savetxt(output_file, new_data, fmt='%.10f', delimiter=' ')
   

    