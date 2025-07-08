# This file is about removing the part where the robot is inactie with a cursor

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.widgets import Cursor

# Set global font for plotting
#rcParams['font.family'] = 'serif'
#rcParams['font.serif'] = ['Palatino Linotype']
rcParams['font.size'] = 22
rcParams['axes.titlesize'] = 24

##### Read the CSV file - Measured motion
root = Path(r"C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/") #Experiments/No_3_Output_files")

files = {
    # "comp-med":    root / "Compensated"  / "2.Medium_complexity_093_robot_UPDATED_compensated.csv",
    # "comp-mean":   root / "Compensated"  / "4.Mean_motion_2_111_robot_UPDATED_compensated.csv",
    # "comp-AP":     root / "Compensated"  / "Lung_Baseline_Shifts_AP_120s_robot_UPDATED_compensated.csv",
    # "comp-SI":     root / "Compensated"  / "Lung_Typical_SI_120s_robot_UPDATED_compensated.csv",
    # "comp-091":    root / "Compensated"  / "Test_motion_091_robot_UPDATED_compensated.csv",
    # "comp-113":    root / "Compensated"  / "Test_motion_113_robot_UPDATED_compensated.csv",
    # "comp-1":      root / "Compensated"  / "Trace 1-Stable target baseline_robot_300s_UPDATED_compensated.csv",
    # "comp-2":      root / "Compensated"  / "Trace 2-Persistant excursion_robot_300s_UPDATED_compensated.csv",
    # "comp-3":      root / "Compensated"  / "Trace 3-Erratic behaviour_robot_300s_UPDATED_compensated.csv",
    # "comp-4":      root / "Compensated"  / "Trace 4-Continuous target drift_robot_300s_UPDATED_compensated.csv",

    # "nc-med":      root / "Not-compensated"  / "2.Medium_complexity_093_robot_UPDATED_nc.csv",
    # "nc-mean":     root / "Not-compensated"  / "4.Mean_motion_2_111_robot_UPDATED_nc.csv",
    # "nc-AP":       root / "Not-compensated"  / "Lung_Baseline_Shifts_AP_120s_robot_UPDATED_nc.csv",
    # "nc-SI":       root / "Not-compensated"  / "Lung_Typical_SI_120s_robot_UPDATED_nc.csv",
    # "nc-091":      root / "Not-compensated"  / "Test_motion_091_robot_UPDATED_nc.csv",
    # "nc-113":      root / "Not-compensated"  / "Test_motion_113_robot_UPDATED_nc.csv",
    # "nc-1":        root / "Not-compensated"  / "Trace 1-Stable target baseline_robot_300s_UPDATED_nc.csv",
    # "nc-2":        root / "Not-compensated"  / "Trace 2-Persistant excursion_robot_300s_UPDATED_nc.csv",
    # "nc-3":        root / "Not-compensated"  / "Trace 3-Erratic behaviour_robot_300s_UPDATED_nc.csv",
    # "nc-4":        root / "Not-compensated"  / "Trace 4-Continuous target drift_robot_300s_UPDATED_nc.csv",
    "test" : root / "Test.csv",
    "test2": root /  "Test_1_0.5mm filter.csv",
}

key      = "test2"              # <-- change this one line
filepath = files[key]
df = pd.read_csv(filepath)
base_name = os.path.splitext(os.path.basename(filepath))[0] # to get the file name for plot title

# Initialize lists to store the data
counts = []
timestamps = [] # SYSTEM_TIME – the PC’s clock taken when the driver receives the frame
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

### Evaluate the offset due to coordinates system center difference between the camera and the robot  
offset =0

distances1_offset = []
for item in distances1:
    distances1_offset.append(-(item - offset))
    
distances2_offset = []
for item in distances2:
    distances2_offset.append((item - offset))
 
timestamps_offset = []
for item in timestamps:
    timestamps_offset.append((item -timestamps[0])/1000)

timestamps_local_offset = []
for item in timestamps_local:
    timestamps_local_offset.append(item -timestamps_local[0])

#### Delete the part where the robot is inactive
cut = {"timestamps": None, "distances1": None}
def on_click(event):
    if event.inaxes:
        cut_time = event.xdata  # get X position (time)
        print(f"Cutting at time = {cut_time:.2f}")

        # Find the closest index
        indexBreak = np.searchsorted(timestamps_offset, cut_time)

        # Trim the data
        cut["timestamps"] = timestamps_offset[indexBreak:]
        cut["timestamps"] = cut["timestamps"] - cut["timestamps"][0]          # shifting the trimmed signal so that its time axis starts at 0

        cut["distances1"] = distances1_offset[indexBreak:]
        # cut["distances1"] = cut["distances1"] - np.mean(cut["distances1"])
        cut["distances1"] = cut["distances1"] - cut["distances1"][0]
        
        fig.canvas.mpl_disconnect(cid)
        plt.close()

fig, ax = plt.subplots(figsize=(20, 8))
ax.plot(timestamps_offset, distances1_offset, label=base_name, color='black')
ax.set_title("Click to place cursor and cut signal before that point")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Motion (mm)")
ax.grid(True)
ax.legend()

cursor = Cursor(ax, horizOn=False, vertOn=True, color='red', linewidth=1.5)
cid = fig.canvas.mpl_connect('button_press_event', on_click)
plt.show()

# # # # Just for debugging
# # with open(r"C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/debug_output.txt", "w") as f:
# #     for val in jumps:
# #         f.write(f"{val}\n")      # True / False on separate lines


#####  Read the TXT file - Input motion
ROOT = Path(r"C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Experiments/No_3_Output_files/Output_files")

FILES = {
    "up-med" :  ROOT / "2.Medium_complexity_093_robot_UPDATED_270625-143235355.txt",
    "up-mean" : ROOT / "4.Mean_motion_2_111_robot_UPDATED_270625-143854323.txt",
    "up-AP" :   ROOT / "Lung_Baseline_Shifts_AP_120s_robot_UPDATED_270625-144535340.txt",
    "up-SI" :   ROOT / "Lung_Typical_SI_120s_robot_UPDATED_270625-144835576.txt",
    "up-091" :  ROOT / "Test_motion_091_robot_UPDATED_270625-145200244.txt",
    "up-113" :  ROOT / "Test_motion_113_robot_UPDATED_270625-145821818.txt",
    "up-1" :    ROOT / "Trace 1-Stable target baseline_robot_300s_UPDATED_010725-154311313.txt",
    "up-2" :    ROOT / "Trace 2-Persistant excursion_robot_300s_UPDATED_270625-151956932.txt",
    "up-3" :    ROOT / "Trace 3-Erratic behaviour_robot_300s_UPDATED_270625-152603977.txt",
    "up-4" :    ROOT / "Trace 4-Continuous target drift_robot_300s_UPDATED_270625-153155239.txt",
}

KEY      = "up-2"              
FILEPATH = FILES[KEY]
DF = pd.read_csv(FILEPATH)
BASENAME = os.path.splitext(os.path.basename(FILEPATH))[0] 

# Lists to store data
timestamp = []
motion = []
 
# Read the file and extract data
with open(FILEPATH, 'r') as file:
    first_line = file.readline()  # reads first line to detect if there is a header
    if any(char.isalpha() for char in first_line):
        pass #skipping of the header
        
    else:
        parts = first_line.strip().split()
        timestamp.append(float(parts[1]))
        motion.append(float(parts[3]))

    # Extract timestamps and motion
    for line in file:
        parts = line.strip().split()
        timestamp.append(float(parts[1]))   # make sure these are the right column number !! (depends on the file type)
        motion.append(float(parts[3]))      # Typically, column 1 and 3 for outpu_files from phantom Control or 0 and 2 for Motion Traces from Github


### Plotting the cut signal and the input trace
plt.figure(figsize=(20, 8))
plt.plot(cut["timestamps"], cut["distances1"], label='Measured motion', color='black')
plt.plot(timestamp, motion, label='Robot Ouput_file')
plt.xlabel("Time (s)")
plt.ylabel("Motion (mm)")
plt.title(base_name)
plt.grid(True)
plt.legend()
plt.tight_layout()

# Saving as a .png
# result_folder = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Experiments/No_3_Output_files/Results'  
# os.makedirs(result_folder, exist_ok=True)            

# results_png = os.path.join(result_folder, f"{base_name}.png")

# plt.savefig(results_png)

plt.show()