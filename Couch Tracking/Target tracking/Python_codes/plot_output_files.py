# this files plot files directly from the output_files folder of the Phantom Control Application

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


##### Read the CSV file - Measured motion
root = Path(r"C:\Users\imagex_labl\Documents\GitHub\1D-couch-applications\Elisa\IntERAct-Release-v1.5\Release\Output Files\6DPlatform")

files = {
    ##### ROBOT MOTION
    "output-med":  root / "2.Medium_complexity_093_robot_UPDATED_270625-143235355.txt",
    "output-mean": root / "4.Mean_motion_2_111_robot_UPDATED_270625-143854323.txt",
    "output-AP":   root / "Lung_Baseline_Shifts_AP_120s_robot_UPDATED_270625-144535340.txt",
    "output-SI":   root / "Lung_Typical_SI_120s_robot_UPDATED_270625-144835576.txt",
    "output-091":  root / "Test_motion_091_robot_UPDATED_270625-145200244.txt",
    "output-113":  root / "Test_motion_113_robot_UPDATED_270625-145821818.txt",
    "output-1":    root / "Trace 1-Stable target baseline_robot_300s_UPDATED_270625-151401911.txt",
    "output-2":    root / "Trace 2-Persistant excursion_robot_300s_UPDATED_270625-151956932.txt",
    "output-3":    root / "Trace 3-Erratic behaviour_robot_300s_UPDATED_270625-152603977.txt",
    "output-4":    root / "Trace 4-Continuous target drift_robot_300s_UPDATED_270625-153155239.txt", 
}

key      = "output-med"              # <-- change this one line
filepath = files[key]
df = pd.read_csv(filepath, sep='\s+', engine='python')

base_name = os.path.splitext(os.path.basename(filepath))[0] # to get the file name for plot title

# Initialize lists to store the data
date = []       # Time(ddMMyy_HHmmssfff)
time = []       # Time(s)
x = []
y = [] 
z = []
rx = []
ry = [] 
rz = [] 

# Iterate over rows in the DataFrame
for index, row in df.iterrows(): 
    # Extract data from each row
    DATE = row['Time(ddMMyy_HHmmssfff)']
    TIME = row['Time(s)']  # Assuming 'Time' is the correct column name for timestamp
    X = row['x(mm)']
    Y = row['y(mm)']
    Z = row['z(mm)']
    RX = row['rx(deg)']
    RY = row['ry(deg)']
    RZ = row['rz(deg)']
   
    # Append data to respective lists
    date.append(DATE)
    time.append(TIME)
    x.append(X)
    y.append(Y)
    z.append(Z)
    rx.append(RX)
    ry.append(RY)
    rz.append(RZ)

# # Just for debugging
# with open(r"C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/debug_output.txt", "w") as f:
#     for val in jumps:
#         f.write(f"{val}\n")      # True / False on separate lines


#####  Read the TXT file - Input mot
ROOT = Path(r"C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Test 27.06/Not-compensated")

FILES = { 
    # "robot-med":   ROOT / "2.Medium_complexity_093_robot.txt",
    # "robot-mean":  ROOT / "4.Mean_motion_2_111_robot.txt",
    # "robot-AP":    ROOT / "Lung_Baseline_Shifts_AP_120s_robot.txt",
    # "robot-SI":    ROOT / "Lung_Typical_SI_120s_robot.txt",
    # "robot-091":   ROOT / "Test_motion_091_robot.txt",
    # "robot-113":   ROOT / "Test_motion_113_robot.txt",
    # "robot-1":     ROOT / "Trace 1-Stable target baseline_robot_300s.txt",
    # "robot-2":     ROOT / "Trace 2-Persistant excursion_robot_300s.txt",
    # "robot-3":     ROOT / "Trace 3-Erratic behaviour_robot_300s.txt",
    # "robot-4":     ROOT / "Trace 4-Continuous target drift_robot_300s.txt",

    ### FILES FROM DEPTH CAMERA
    "up-med":      ROOT  /  "2.Medium_complexity_093_robot_UPDATED_nc.csv",
    "up-mean":     ROOT  /  "4.Mean_motion_2_111_robot_UPDATED_nc.csv",
    "up-AP":       ROOT  /  "Lung_Baseline_Shifts_AP_120s_robot_UPDATED_nc.csv",
    "up-SI":       ROOT  /  "Lung_Typical_SI_120s_robot_UPDATED_nc.csv",
    "up-091":      ROOT  /  "Test_motion_091_robot_UPDATED_nc.csv",
    "up-113":      ROOT  /  "Test_motion_113_robot_UPDATED_nc.csv",
    "up-1":        ROOT  /  "Trace 1-Stable target baseline_robot_300s_UPDATED_nc.csv",
    "up-2":        ROOT  /  "Trace 2-Persistant excursion_robot_300s_UPDATED_nc.csv",
    "up-3":        ROOT  /  "Trace 3-Erratic behaviour_robot_300s_UPDATED_nc.csv",
    "up-4":        ROOT  /  "Trace 4-Continuous target drift_robot_300s_UPDATED_nc.csv",
    
}

KEY      = "up-med"              
FILEPATH = FILES[KEY]
DF = pd.read_csv(FILEPATH)
BASENAME = os.path.splitext(os.path.basename(FILEPATH))[0] 


##### For .TXT files
# # Lists to store data
# timestamp = []
# motion = []
 
# # Read the file and extract data
# with open(FILEPATH, 'r') as file:
#     for line in file:
#         parts = line.strip().split()
#         if len(parts) == 7:
#             timestamp.append(float(parts[0]))
#             motion.append(float(parts[2]))
#####

##### For .CSV files
# Initialize lists to store the data
counts = []
timestamps = [] # SYSTEM_TIME – the PC’s clock taken when the driver receives the frame
timestamps_local = []
distances1 = [] # ROI1
distances2 = [] # ROI2
 
# Iterate over rows in the DataFrame
for index, row in DF.iterrows(): 
    #print(row)
    # Extract data from each row
    count = row['Count']
    timestamp = row['Time']  # Assuming 'Time' is the correct column name for timestamp
    timestamp_local = row[' Local Time']
    distance1 = row[' Distance 1']
    distance2 = row[' Distance 2']
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

# Plotting
plt.figure(figsize=(20, 8))
plt.plot(time, y, color='black', label='Robot motion')
plt.plot(timestamps, distances1, label='Camera data')
plt.xlabel('Time (s)')#,  fontsize=16)   
plt.ylabel('Motion (mm)')#, fontsize=16) 
plt.title(BASENAME)#,     fontsize=20)  
plt.legend()               
plt.grid(True)
plt.tight_layout()

# Saving as a .png
result_folder = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Test 27.06'  
os.makedirs(result_folder, exist_ok=True)            

results_png = os.path.join(result_folder, f"{BASENAME}.png")

plt.savefig(results_png)

plt.show()