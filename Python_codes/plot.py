# This file is about plotting the input traces and the compensate movement on the same graph to 
# highlight the action of the compensiation algorithm and evaluate its performances

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.close('all')

##### Plot CSV files (_robot)
# Read the CSV file - Compensated motion
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Compensated/2.Medium_complexity_093_robot_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Compensated/4.Mean_motion_2_111_robot_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Compensated/Lung_Baseline_Shifts_AP_120s_robot_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Compensated/Lung_Baseline_Shifts_combined_robot_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Compensated/Lung_Typical_SI_120s_robot_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Compensated/nomotion_compensated.csv'
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Compensated/Test_motion_091_robot_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Compensated/Test_motion_113_robot_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Compensated/Trace 1-Stable target baseline_robot_300s_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Compensated/Trace 2-Persistant excursion_robot_300s_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Compensated/Trace 3-Erratic behaviour_robot_300s_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Compensated/Trace 4-Continuous target drift_robot_300s_compensated.csv'

# Read the CSV file - Not Compensated motion
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Not-compensated/2.Medium_complexity_093_robot_not_compensated.csv'
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Not-compensated/4.Mean_motion_2_111_robot_not_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Not-compensated/Lung_Baseline_Shifts_AP_120s_robot_not_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Not-compensated/Lung_Baseline_Shifts_combined_robot_not_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Not-compensated/Lung_Typical_SI_120s_robot_not_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Not-Compensated/nomotion_not_compensated.csv'
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Not-compensated/Test_motion_091_robot_not_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Not-compensated/Test_motion_113_robot_not_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Not-compensated/Trace 1-Stable target baseline_robot_300s_not_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Not-compensated/Trace 2-Persistant excursion_robot_300s_not_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Not-compensated/Trace 3-Erratic behaviour_robot_300s_not_compensated.csv' 
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Not-compensated/Trace 4-Continuous target drift_robot_300s_not_compensated.csv' 
filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/30.06.25/2.Medium_complexity_093_robot_UPDATED_comp.csv'
#filepath = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/30.06.25/test.csv'

df = pd.read_csv(filepath)
print(df.columns)
base_name = os.path.splitext(os.path.basename(filepath))[0]

# Initialize lists to store the data
counts = []
timestamps = []
timestamps_local = []
distances1 = [] # ROI1
distances2 = [] # ROI2
 
# Iterate over rows in the DataFrame
for index, row in df.iterrows(): 
    #print(row)
    # Extract data from each row
    count = row['Count']
    timestamp = row['Time']  # Assuming 'Time' is the correct column name for timestamp
    timestamp_local = row['Local Time']
    distance1 = row['Distance 1']
    distance2 = row['Distance 2']
    '''
    # Check if 'Distance 2' exists in the DataFrame
    if 'Distance 2' in df.columns:
        distance2 = row[' Distance 2']
    else:
        distance2 = None  # Set distance2 to None if the column doesn't exist
    '''
    # Append data to respective lists
    counts.append(count)
    timestamps.append(timestamp)
    timestamps_local.append(timestamp_local)
    distances1.append(distance1)
    distances2.append(distance2)
 
# Convert each value back to actual time in seconds
actual_time_array = [value * 0.1 for value in counts]


# # Just for debugging
with open(r"C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/debug_output.txt", "w") as f:
    for val in timestamps:
        f.write(f"{val}\n")      # True / False on separate lines



# Delete the part where the robot is inactive 
# indexBreak = 0
# counts = counts[indexBreak:]
# timestamps = timestamps[indexBreak:]
# distances1 = distances1[indexBreak:]
# distances2 = distances2[indexBreak:]
# '''
# # For verification
# for i in range(len(counts)):
#     if distances1[i] != pi_depth[i]:
#         print("Error in transmission")
# '''
 
# distances1_offset = []
# for item in distances1:
#     distances1_offset.append(-(item -507))
    
# distances2_offset = []
# for item in distances2:
#     distances2_offset.append((item - 507))
 
timestamps_offset = []
for item in timestamps:
    timestamps_offset.append((item -timestamps[0])/1000)
 
# plt.plot(timestamps,distances1, color='black', label='Count vs Distance 2')
# plt.xlabel('Time (s)')
# plt.ylabel('Displacement (mm)')
# plt.title(base_name)
# #plt.legend()
# plt.grid(True)

 
##### Plot .txt files

# File path, input traces
file_path = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Motion Traces/2.Medium_complexity_093_robot.txt'  # Replace with your actual filename
#file_path = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Input_traces/4.Mean_motion_2_111_robot.txt' 
#file_path = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Input_traces/Lung_Baseline_Shifts_AP_120s_robot.txt' 
#file_path = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Input_traces/Lung_Baseline_Shifts_combined_robot.txt' 
#file_path = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Input_traces/Lung_Typical_SI_120s_robot.txt' 
#file_path = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Input_traces/Test_motion_091_robot.txt' 
#file_path = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Input_traces/Test_motion_113_robot.txt' 
#file_path = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Input_traces/Trace 1-Stable target baseline_robot_300s.txt' 
#file_path = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Input_traces/Trace 2-Persistant excursion_robot_300s.txt' 
#file_path = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Input_traces/Trace 3-Erratic behaviour_robot_300s.txt' 
#file_path = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Input_traces/Trace 4-Continuous target drift_robot_300s.txt' 

#Lists to store data
timestamp = []
motion = []
 
# Read the file and extract data
with open(file_path, 'r') as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) == 7:
            timestamp.append(float(parts[0]))
            motion.append(float(parts[2]))

# Plotting
plt.figure(figsize=(20, 8))
plt.plot(timestamps_offset,distances1, color='black', label='Measured motion')
plt.plot(timestamp, motion, label='Input trace')
plt.xlabel('Time (s)',  fontsize=16)   
plt.ylabel('Motion (mm)', fontsize=16) 
plt.title(base_name,     fontsize=20)  
plt.legend(fontsize=16)               
plt.grid(True)
plt.tight_layout()

## Saving as a .png
# result_folder = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Results'  
# os.makedirs(result_folder, exist_ok=True)            

# results_png = os.path.join(result_folder, f"{base_name}.png")

# plt.savefig(results_png)

plt.show()