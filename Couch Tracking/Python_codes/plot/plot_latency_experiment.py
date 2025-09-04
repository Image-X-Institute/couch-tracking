# This file should plot the couch's motion and the robot's motion, both captured by the 
# realsense depth camera
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
KEY ="step_5-1" # <-- change this one line
FILEPATH = FILES[KEY]
camera = pd.read_csv(FILEPATH)
BASE_NAME = os.path.splitext(os.path.basename(FILEPATH))[0] # to get the file name for plot title

# Convertion of Time() to seconds
camera['Time_sec'] = camera['Time(ddMMyy_HHmmssfff_format)'].str.split('_').str[1].astype(float)

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

camera['Time_sec'] = camera['Time_sec'].apply(timefloat_to_seconds)

start = camera['Time_sec'].iloc[0]
camera['Time_sec'] = camera['Time_sec'] - start
# print(camera["Time_sec"])

# Plot the two files
plt.figure(figsize=(1, 8))
plt.plot(camera["Time_sec"], camera["Distance 1"], label='Target motion', color='blue')
plt.plot(camera["Time_sec"], camera["Distance 2"], label='Couch\'s motion', color='black')
plt.xlabel("Time (s)", fontsize=20)
plt.ylabel("Motion (mm)", fontsize=20)
plt.title(BASE_NAME, fontsize=24)
plt.grid(True)
plt.legend(fontsize=20)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.tight_layout()


# Saving as a .png
# result_folder = 'C:/Users/imagex_labl/Documents/GitHub/1D-robot-applications/Elisa/Experiments/No_5_final/Results_bis'  
# os.makedirs(result_folder, exist_ok=True)            

# results_png = os.path.join(result_folder, f"{BASE_NAME}.png")

# plt.savefig(results_png)

plt.show()