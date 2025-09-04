import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set global font to Palatino Linotype
# rcParams['font.family'] = 'serif'
# rcParams['font.serif'] = ['Palatino Linotype']

# # Optional: adjust font size globally
# rcParams['font.size'] = 12

# # Test plot
# plt.plot([1, 2, 3], [1, 4, 9])
# plt.title("Plot Title")
# plt.xlabel("X Axis")
# plt.ylabel("Y Axis")
# plt.grid(True)
# plt.show()

# # # Just for debugging
# with open(r"C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/debug_output.txt", "w") as f:
#     for val in jumps:
#         f.write(f"{val}\n")      # True / False on separate lines

##
import struct

# # Raw byte stream (from your example)
# byte_stream = bytes([99, 0, 0, 32, 65, 116, 0, 97, 158, 71])  # 'c' and 't' markers + 2 floats

# # Extract float value for count (bytes 1-4)
# count_bytes = byte_stream[1:5]
# count_value = struct.unpack('<f', count_bytes)[0]

# # Extract float value for depth (bytes 6-9)
# depth_bytes = byte_stream[6:10]
# depth_value = struct.unpack('<f', depth_bytes)[0]

# print(f"Decoded count value: {count_value}")
# print(f"Decoded depth value: {depth_value}")



######################################################################
# PLot latency experment with robot 
# This file should match timestamp and plot the signals for couch log files

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ########## DEPTH CAMERA DATA
# ROOT = Path(r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_6_Latency\camera")
# FILES = {
#     "AP":           ROOT / "Lung_Baseline_Shifts_AP_120s_robot_replicated4.csv",
#     "flipped-AP":   ROOT / "Lung_Baseline_Shifts_AP_120s_robot_replicated4flipped.csv",
#     "flipped-3":    ROOT / "sin_3_replicatedflipped.csv",
#     "flipped-5":    ROOT / "sin_5_replicatedflipped.csv",
#     "flipped-8":    ROOT / "sin_8_replicatedflipped.csv",
#     "flipped-13":   ROOT / "sin_13_replicatedflipped.csv",
#     }
# KEY = "flipped-3" # <-- change this one line
# FILEPATH = FILES[KEY]
# camera = pd.read_csv(FILEPATH)
# BASE_NAME = os.path.splitext(os.path.basename(FILEPATH))[0] # to get the file name for plot title

# ######### COUCH LOG FILES
# root = Path(r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_6_Latency\log_files")
# files = {
#     "couch-AP":  root / "depth_latency_UDP_Lung_Baseline_Shifts_AP_replicated4.csv",
#     "couch-3":   root / "depth_latency_UDP_sin_3.csv",
#     "couch-5":   root / "depth_latency_UDP_sin_5.csv",
#     "couch-8":   root / "depth_latency_UDP_sin_8.csv",
#     "couch-13":  root / "depth_latency_UDP_sin_13.csv",
#     }
# key  = "couch-3" # <-- change this one line
# filepath = files[key]
# couch = pd.read_csv(filepath)

# ######## ROBOT OUTPUT_FILES
# Root = Path(r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_6_Latency\output_files")
# Files = {
#     "robot-AP":  Root / "depth_latency_UDP_Lung_Baseline_Shifts_AP_replicated4.txt",
#     "robot-3":   Root / "sin_3_240725-132333804.txt",
#     "robot-5":   Root / "sin_5_240725-132551480.txt",
#     "robot-8":   Root / "sin_8_240725-132756163.txt",
#     "robot-13":  Root / "sin_13_240725-133000690.txt",
#     }
# Key  = "robot-3" # <-- change this one line
# Filepath = Files[Key]
# robot = pd.read_csv(Filepath, sep=r'\s+', header=0)

# # Conversion of ddMMyy_HHmmssfff to seconds
# def timefloat_to_seconds(t):
#     # Convert float or int to zero-padded string of length 9 (HHmmssfff)
#     s = f"{int(t):09d}"  # e.g. 125838275 -> "125838275"
    
#     HH = int(s[0:2])
#     mm = int(s[2:4])
#     ss = int(s[4:6])
#     fff = int(s[6:9])
    
#     total_seconds = HH * 3600 + mm * 60 + ss + fff / 1000
#     return total_seconds


# # # Extraction of the time in ddMMyy_HHmmssfff, conversion from string to float
# robot['Time_float'] = robot['Time(ddMMyy_HHmmssfff_format)'].str.split('_').str[1].astype(float)
# robot['Seconds'] = robot['Time_float'].apply(timefloat_to_seconds)

# # Conversion in seconds
# # couch['Timestamp'] is in microseconds
# # camera['Time'] is in miliseconds

# couch['Timestamp'] = couch['Timestamp']/1000000
# camera['Time'] = camera['Time']/1000

# # Matching of timestamps
# # Get the first timestamp of the robot (robot starts moving)
# robot_start = robot['Seconds'].iloc[0]

# camera['Time_aligned'] = camera['Time'] - robot_start 
# couch['Time_aligned'] = couch['Timestamp'] - robot_start


# # print(camera['Time_aligned'].iloc[0])
# # print(couch['Time_aligned'].iloc[0])
# # latency = camera['Time_aligned'].iloc[0]-couch['Time_aligned'].iloc[0]
# latency = 1753327408076300/1000000 - 1753327414311.01/1000
# print(f"Latency = {latency} s")

# latency2 = camera['Time_aligned'].iloc[0]-couch['Time_aligned'].iloc[0]
# print(f"Latency2 = {latency2} s")
# print(robot_start)


# Plot the two files
# plt.figure(figsize=(17, 8))
# plt.plot(camera["Time_aligned"], camera["Distance 1"], label='replicated motion', color='blue')
# plt.plot(couch["Time_aligned"], couch["Adjusted_position"], label='couch\'s motion', color='black')
# plt.xlabel("Time (s)", fontsize=20)
# plt.ylabel("Motion (mm)", fontsize=20)
# plt.title(BASE_NAME, fontsize=24)
# plt.grid(True)
# plt.legend(fontsize=20)
# plt.xticks(fontsize=20)
# plt.yticks(fontsize=20)
# plt.tight_layout()


# Saving as a .png
# result_folder = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Experiments/No_5_final/Results_bis'  
# os.makedirs(result_folder, exist_ok=True)            

# results_png = os.path.join(result_folder, f"{BASE_NAME}.png")

# plt.savefig(results_png)

# # plt.show()
# import os
# import re

# # Folder containing your files
# folder = r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_7_emulator\integrated emulator\test"

# for filename in os.listdir(folder):
#     old_path = os.path.join(folder, filename)

#     if not os.path.isfile(old_path):
#         continue

#     # Match the first "number + ms" that appears after "_local_"
#     match = re.search(r'(_local_)([0-9.]+)ms', filename)
#     if match:
#         # Extract the number
#         value_ms = float(match.group(2))
#         # Convert to seconds (multiply by 1000)
#         value_s = int(value_ms * 1000)
#         # Build new filename
#         new_filename = filename.replace(match.group(0), f"{match.group(1)}{value_s}ms", 1)

#         new_path = os.path.join(folder, new_filename)
#         os.rename(old_path, new_path)
#         print(f"Renamed:\n  {old_path}\n→ {new_path}\n")

print(round(0.9945,2))