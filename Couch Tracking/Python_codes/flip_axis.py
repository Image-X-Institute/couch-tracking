# Turns he signal upside down o it represented the robot actual motion

import numpy as np
import os
import glob
import pandas as pd

# Folder with input .txt files to flip axis
input_folder = r"C:\Users\imagex_labl\Documents\GitHub\1D-couch-applications\Elisa\Experiments\No_5_final\t"

# Output folder
output_folder = r"C:\Users\imagex_labl\Documents\GitHub\1D-couch-applications\Elisa\Experiments\No_5_final\flipped_camera"  
os.makedirs(output_folder, exist_ok=True)  # Create folder if it doesn't exist

file_pattern = os.path.join(input_folder, '*.csv') 

# Browse all files
for file_path in glob.glob(file_pattern):
    filename = os.path.basename(file_path)
    df = pd.read_csv(file_path, sep=',', engine='python')

    df['Distance 1'] = -df['Distance 1']  # Flip X axis
    df['Distance 2'] = -df['Distance 2']  # Flip Y axis
    #df['z(mm)'] = -df['z(mm)']  # Flip Z axis

    # Reconstruct and save new data
    output_file = os.path.join(output_folder, filename.replace('.csv', '.csv'))
    df.to_csv(output_file, sep=',', index=False)
    print(f"✔️ {filename} -> {output_file}")


    