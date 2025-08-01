# This file should match timestamp and plot the signals for robot log files

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

########## DEPTH CAMERA DATA files
ROOT = Path(r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_6_latency\compensation")
FILES = {
   "test" : ROOT/"test.csv",        
   "step_3-1" : ROOT /"step_3-1.csv",
   "step_3-2" : ROOT /"step_3-2.csv",
   "step_3-3" : ROOT /"step_3-3.csv",
   "step_5-1" : ROOT /"step_5-1.csv",
   "step_5-2" : ROOT /"step_5-2.csv",
   "step_5-3" : ROOT /"step_5-3.csv",
   "step_7-1" : ROOT /"step_7-1.csv",
   "step_7-2" : ROOT /"step_7-2.csv",
   "step_7-3" : ROOT /"step_7-3.csv",
    }
KEY ="step_7-1" # <-- change this one line
FILEPATH = FILES[KEY]
camera = pd.read_csv(FILEPATH)
BASE_NAME = os.path.splitext(os.path.basename(FILEPATH))[0] # to get the file name for plot title

# Conversion of ddMMyy_HHmmssfff to seconds
def timefloat_to_seconds(t):
    # Convert float or int to zero-padded string of length 9 (HHmmssfff)
    s = f"{int(t):09d}"  # e.g. 125838275 ->"125838275"
    
    HH = int(s[0:2])
    mm = int(s[2:4])
    ss = int(s[4:6])
    fff = int(s[6:9])
    
    total_seconds = HH * 3600 + mm * 60 + ss + fff / 1000
    return total_seconds
camera['Time_sec'] = camera['Time(ddMMyy_HHmmssfff_format)'].str.split('_').str[1].astype(float).apply(timefloat_to_seconds)

start = camera['Time_sec'].iloc[0]
camera['Time_sec'] = camera['Time_sec'] - start

######### ROBOT OUTPUT FILES - for the target
root = Path(r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_6_latency\compensation\output_files")
files = {
    "step_3-1" : root /"step_3_UPDATED-1_310725-120134977.txt",
    "step_3-2" : root /"step_3_UPDATED-2_310725-120853900.txt",
    "step_3-3" : root /"step_3_UPDATED-3_310725-121102568.txt",
    "step_5-1" : root /"step_5_UPDATED-1_310725-120339149.txt",
    "step_5-2" : root /"step_5_UPDATED-2_310725-121255357.txt",
    "step_5-3" : root /"step_5_UPDATED-3_310725-130637168.txt",
    "step_7-1" : root /"step_7_UPDATED-1_310725-120538896.txt",
    "step_7-2" : root /"step_7_UPDATED-2_310725-130853285.txt",
    "step_7-3" : root /"step_7_UPDATED-3_310725-131117034.txt",
    }
key  = "step_7-1" # <-- change this one line
filepath = files[key]
robot = pd.read_csv(filepath, sep=' ')

robot['Time_sec']= robot['Time(ddMMyy_HHmmssfff_format)'].str.split('_').str[1].astype(float).apply(timefloat_to_seconds)
robot['Time_sec'] = robot['Time_sec'] - start

# print(robot['Timestamp'].iloc[0])

# Conversion in seconds
# robot['Timestamp'] is in microseconds
# camera['Time'] is in miliseconds


# robot['Time_sec'] = robot['Timestamp']/1000000 - start
# camera['Time_sec'] = camera['Time']/1000 - start


# print(camera['Time_sec'].iloc[0])
# print(robot['Time_sec'].iloc[0])


# latency = camera['Time_sec'].iloc[0]-robot['Time_sec'].iloc[0]
# print(f"Latency = {latency} s")

# print(start)

# Plot robot's output file, couch's position and target's position
# plt.figure(figsize=(17, 8))
# plt.plot(camera["Time_sec"], -camera["Distance 1"], label='Target motion', color='blue')
# plt.plot(camera["Time_sec"], -camera["Distance 2"], label='Couch\'s motion', color='black')
# plt.plot(robot['Time_sec'], robot["y(mm)"], label = "robot's motion", color = "green")
# plt.xlabel("Time (s)", fontsize=20)
# plt.ylabel("Motion (mm)", fontsize=20)
# plt.title(BASE_NAME, fontsize=24)
# plt.grid(True)
# plt.legend(fontsize=20)
# plt.xticks(fontsize=20)
# plt.yticks(fontsize=20)
# plt.tight_layout()



fig, ax = plt.subplots(figsize=(10, 8))  # Create fig and ax properly

# Add Cursor on ax
# cursor = Cursor(ax, useblit=True, color='green', linewidth=1, vertOn=True, horizOn=False)

# Your plot commands
# ax.plot(camera["Time_sec"], -camera["Distance 1"], label='Target motion', color='blue')
ax.plot(camera["Time_sec"], -camera["Distance 2"], label="Couch's motion", color='black')
ax.plot(robot['Time_sec'], robot["y(mm)"], label="Robot's motion", color="green")

x_pos = 6.557           # robot
x_pos2 = 7.572          # couch

ax.axvline(x=x_pos, color='red', linestyle='--', linewidth=2)
plt.text(4.20, 7.14, f"{x_pos:.3f}s", rotation=0, color='red', fontsize=20)

ax.axvline(x=x_pos2, color='red', linestyle='--', linewidth=2)
plt.text(8.18, -8.71, f"{x_pos2:.3f}s", rotation=0, color='red', fontsize=20)
# Labels and formatting
ax.set_xlabel("Time (s)", fontsize=16)
ax.set_ylabel("Motion (mm)", fontsize=16)
ax.set_title(BASE_NAME, fontsize=24)
ax.grid(True)
ax.legend(fontsize=18)
ax.tick_params(axis='both', labelsize=16)
fig.tight_layout()


# # Saving as a .png
# # result_folder = 'C:/Users/imagex_labl/Documents/GitHub/1D-robot-applications/Elisa/Experiments/No_5_final/Results_bis'  
# # os.makedirs(result_folder, exist_ok=True)            

# # results_png = os.path.join(result_folder, f"{BASE_NAME}.png")

# # plt.savefig(results_png)

plt.show()