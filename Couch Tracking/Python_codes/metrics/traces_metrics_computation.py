# This script aims to analyse input traces (position as a function of time) by computing metrics such as
# the RMSE (Root Mean Square Error) and the MAE (Mean Absolute Error), Standard deviation, 95th and 5th percentile
import os
import pandas as pd
import numpy as np
import glob
from sklearn.metrics import root_mean_squared_error, mean_absolute_error

# Folders of the original traces 
folder = r"C:\Users\imagex_labl\Documents\Elisa\Experiments\Latency measurement\step_traces\step_updated"


# Forlder to save data
output_folder = r"C:\Users\imagex_labl\Documents\Elisa\Experiments\Latency measurement\step_traces"
os.makedirs(output_folder, exist_ok=True)  # create new folder 

# Get all the files that end with ".csv" or ".txt"
### UNCOMMENT IF CSV FILES
# comp_file_pattern = os.path.join(folder, '*comp.csv')

### UNCOMMENT IF TXT FILES
comp_file_pattern = os.path.join(folder, '*.txt')


results = []

for path in glob.glob(comp_file_pattern):
    filename = os.path.splitext(os.path.basename(path))[0].replace('-*', ' ') # to get the trace's name, adapt to your filename structure

    # # To compare to an original file
    # original_path = os.path.join(original_folder, filename +'_UPDATED.txt')
    # if not os.path.exists(original_path):
    #     print(f"Compensated file not found for: {filename + '_UPDATED.txt'}")
    #     continue

    ### UNCOMMENT IF CSV FILES
    # comp_trace = pd.read_csv(path)
    # dist1 = comp_trace["Distance 1"]

    ### UNCOMMENT IF TXT FILES
    original_trace = pd.read_csv(path, sep='\s+', header=None)  # No header in file
    dist1 = original_trace.iloc[:, 2]  # 3rd column
    time = original_trace.iloc[:,0]

    ## To compare to zero 
    zero_vector = np.zeros_like(abs(dist1))
    
    # Compute RMSE
    RMSE = root_mean_squared_error(zero_vector, abs(dist1))  

    # Compute MAE
    MAE = mean_absolute_error(zero_vector,abs(dist1))

    # Compute max and min values
    maxi = float(max(dist1))
    mini = float(min(dist1))

    # Motion range
    motion_range = float(abs(maxi-mini))

    # Maximum speed
    speed = np.gradient(dist1, time)
    max_speed = max(abs(speed))
    
    # Maximum acceleration
    acceleration = np.gradient(speed,time)   
    max_acceleration = max(abs(acceleration))

    # Standard deviation 
    std_dev = np.std(abs(dist1), ddof=1)

    # 5th percentile - motion
    p5 = np.percentile(abs(dist1), 15)

    # 95th percentile - motion
    p95 = np.percentile(abs(dist1), 95)

    # 5th percentile - speed
    p10_speed = np.percentile(abs(speed), 10)

    # 95th percentile - speed
    p90_speed = np.percentile(abs(speed), 90)

    # keep only the metrics you want
    results.append([filename, round(max_speed, 1), round(max_acceleration, 1)] )    
    # results.append([filename, round(MAE, 1), round(std_dev, 1), round(maxi, 1),round(mini, 1), round(p5, 1), round(p95, 1)] )    

# Create DataFrame and save
df = pd.DataFrame(results, columns=["Trace", "Max speed (mm/s)", "Max acceleration (mm/s2)"]) 
# df = pd.DataFrame(results, columns=["Trace", "MAE (mm)", "Standard deviation (mm)", "Max (mm)", "Min (mm)", "5th percentile (mm)", "95th percentile (mm)" ]) # keep only the metrics you want

output_filename = "step_traces_analysis.csv"
output_file = os.path.join(output_folder, output_filename)
df.to_csv(output_file, index=False)

print(f"{output_filename} saved here : {output_folder}")