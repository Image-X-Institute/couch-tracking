# This script convert 6 DOF traces into 1D traces by keeping the largest motion and putting everything else at 0

import numpy as np
import os
import glob

# Folder with input .txt files
input_folder = r"C:\Users\imagex_labl\Documents\GitHub\1D-couch-applications\Elisa\Experiments\Motion Traces\new_traces_6DOF"
# Output folder
output_folder = r"C:\Users\imagex_labl\Documents\GitHub\1D-couch-applications\Elisa\Experiments\Motion Traces\new_traces_1D"
os.makedirs(output_folder, exist_ok=True)  # Create if it doesn't exist

file_pattern = os.path.join(input_folder, '*.txt') 

# Browse all files
for file_path in glob.glob(file_pattern):
    filename = os.path.basename(file_path)

    # Load data
    data = np.loadtxt(file_path)

    if data.shape[1] == 7:
        # Extract time and motion to be kept
        time = data[:, 0]
        motion = data[:, 2]
        zeros = np.zeros_like(time)
    
    elif data.shape[1] == 2:
        # Extract time and motion to be kept
        time = data[:, 0]
        motion = data[:, 1]
        zeros = np.zeros_like(time)
         
    else:
        print(f"⚠️ Unexpected number of columns in {file_path}: {data.shape[1]}, file skiped")
        continue     

    # Reconstruct and save new data
    new_data = np.column_stack((time, zeros, motion, zeros, zeros, zeros, zeros))    
    
    # Center all columns EXCEPT time (column 0)
    # mean_values = new_data[:, 2].mean(axis=0)
    # new_data[:, 2] -= mean_values

    output_file = os.path.join(output_folder, filename.replace('.txt', '_1D.txt'))
    np.savetxt(output_file, new_data, fmt='%.4f', delimiter=' ')
    print(f"✔️ {filename} -> {output_folder}")

   
   

    