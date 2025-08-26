# This script aims to analyse input traces (position as a function of time) and compensated motion traces to calcuates 
# the RMSE (Root Mean Square Error) and the MAE (Mean Absolute Error), Standard deviation, 95th and 5th percentile
import os
import pandas as pd
import numpy as np
import glob
from sklearn.metrics import root_mean_squared_error, mean_absolute_error

# Folders of the original traces and the compensated motion
# original_folder = r"C:\Users\imagex_labl\Documents\GitHub\1D-couch-applications\Elisa\Experiments\No_5_final\robot_files"
compensated_folder = r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_6_latency\compensation\camera"
#r"C:\Users\imagex_labl\Documents\Elisa\Experiments\updated_files"


# Forlder to save data
output_folder = r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_6_latency\compensation"
os.makedirs(output_folder, exist_ok=True)  # create new folder 

# Get all the files that end with ".csv"
comp_file_pattern = os.path.join(compensated_folder, '*.csv')
results = []

for path in glob.glob(comp_file_pattern):
    filename = os.path.splitext(os.path.basename(path))[0].replace('-*', ' ') # to get the trace's name
    comp_trace = pd.read_csv(path)
    dist1 = comp_trace["Distance 1"]

    # # To compare to an original file
    # original_path = os.path.join(original_folder, filename +'_UPDATED.txt')
    # if not os.path.exists(original_path):
    #     print(f"Compensated file not found for: {filename + '_UPDATED.txt'}")
    #     continue
    # original_trace = pd.read_csv(path, sep='\s+', header=None)  # No header in file
    # dist1 = original_trace.iloc[:, 2]  # 3rd column
    
    ## To compare to zero 
    zero_vector = np.zeros_like(abs(dist1))
    
    # Compute RMSE
    RMSE = root_mean_squared_error(zero_vector, abs(dist1))  

    # Compute MAE
    MAE = mean_absolute_error(zero_vector,abs(dist1))

    # Compute max and min values
    maxi = float(max(dist1))
    mini = float(min(dist1))
    motion_range = float(abs(maxi-mini))

    # Standard deviation 
    std_dev = np.std(abs(dist1), ddof=1)
    # 5th percentile 
    p5 = np.percentile(abs(dist1), 15)
    # 95th percentile 
    p95 = np.percentile(abs(dist1), 95)

    results.append([filename, round(MAE, 2), round(std_dev, 2), round(maxi, 2),round(mini, 2), round(p95, 2), round(p5, 2)] )    

# Create DataFrame and save
df = pd.DataFrame(results, columns=["Trace", "MAE (mm)", "Standard deviation (mm)", "Max (mm)", "Min (mm)", "95th percentile (mm)", "5th percentile (mm)" ])

output_filename = "step_traces_analysis_comp.csv"
output_file = os.path.join(output_folder, output_filename)
df.to_csv(output_file, index=False)

print(f"{output_filename} saved here : {output_folder}")