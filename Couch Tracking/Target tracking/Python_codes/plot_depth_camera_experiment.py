# This file should match timestamp and plot the signals

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

########## DEPTH CAMERA DATA
ROOT = Path(r"C:/Users/imagex_labl/Documents/Elisa/Experiments")
FILES = {
    "test" : ROOT/"test.csv",    
    # "comp-med":  ROOT / "2.Medium_complexity_093_robot_UPDATED_comp.csv",
    # "nc-med":    ROOT / "2.Medium_complexity_093_robot_UPDATED_nc.csv",

    # "comp-mean": ROOT / "4.Mean_motion_2_111_robot_UPDATED_comp.csv",
    # "nc-mean":   ROOT / "4.Mean_motion_2_111_robot_UPDATED_nc.csv",

    # "comp-AP":   ROOT / "Lung_Baseline_Shifts_AP_120s_robot_UPDATED_comp.csv",
    # "nc-AP":     ROOT / "Lung_Baseline_Shifts_AP_120s_robot_UPDATED_nc.csv",

    # "comp-SI":   ROOT / "Lung_Typical_SI_120s_robot_UPDATED_comp.csv",
    # "nc-SI":     ROOT / "Lung_Typical_SI_120s_robot_UPDATED_nc.csv",

    # "comp-091":  ROOT / "Test_motion_091_robot_UPDATED_comp.csv",
    # "nc-091":    ROOT / "Test_motion_091_robot_UPDATED_nc.csv",

    # "comp-113":  ROOT / "Test_motion_113_robot_UPDATED_comp.csv",
    # "nc-113":    ROOT / "Test_motion_113_robot_UPDATED_nc.csv",

    # "comp-1":    ROOT / "Trace 1-Stable target baseline_robot_300s_UPDATED_comp.csv",
    # "nc-1":      ROOT / "Trace 1-Stable target baseline_robot_300s_UPDATED_nc.csv",

    # "comp-2":    ROOT / "Trace 2-Persistant excursion_robot_300s_UPDATED_comp.csv",
    # "nc-2":      ROOT / "Trace 2-Persistant excursion_robot_300s_UPDATED_nc.csv",

    # "comp-3":    ROOT / "Trace 3-Erratic behaviour_robot_300s_UPDATED_comp.csv",
    # "nc-3":      ROOT / "Trace 3-Erratic behaviour_robot_300s_UPDATED_nc.csv",
    
    # "comp-4":    ROOT / "Trace 4-Continuous target drift_robot_300s_UPDATED_comp.csv",
    # "nc-4":      ROOT / "Trace 4-Continuous target drift_robot_300s_UPDATED_nc.csv",
    # "test": ROOT/"Lung_Baseline_Shifts_AP_120s_robot_replicated4flipped.csv"

    }
KEY = "test" # <-- change this one line
FILEPATH = FILES[KEY]
camera = pd.read_csv(FILEPATH)
BASE_NAME = os.path.splitext(os.path.basename(FILEPATH))[0] # to get the file name for plot title


######### OUTPUT FILES ROBOT
root = Path(r"C:\Users\imagex_labl\Documents\Elisa\IntERAct-Release-v1.5\Release\Output Files\6DPlatform")
files = {
    "test" : root /"Lung_Baseline_Shifts_AP_120s_robot_UPDATED_310725-105358026.txt"
    # "comp-med":  root / "2.Medium_complexity_093_robot_UPDATED_070725-103501311.txt",
    # "nc-med":    root / "2.Medium_complexity_093_robot_UPDATED_070725-104803728.txt",

    # "comp-mean": root / "4.Mean_motion_2_111_robot_UPDATED_070725-150244411.txt",
    # "nc-mean":   root / "4.Mean_motion_2_111_robot_UPDATED_070725-150817333.txt",

    # "comp-AP":   root / "Lung_Baseline_Shifts_AP_120s_robot_UPDATED_070725-112657138.txt",
    # "nc-AP":     root / "Lung_Baseline_Shifts_AP_120s_robot_UPDATED_070725-113040641.txt",

    # "comp-SI":   root / "Lung_Typical_SI_120s_robot_UPDATED_070725-113328055.txt",
    # "nc-SI":     root / "Lung_Typical_SI_120s_robot_UPDATED_070725-113606533.txt",

    # "comp-091":  root / "Test_motion_091_robot_UPDATED_070725-151527321.txt",
    # "nc-091":    root / "Test_motion_091_robot_UPDATED_070725-152219424.txt",

    # "comp-113":  root / "Test_motion_113_robot_UPDATED_070725-152802538.txt",
    # "nc-113":    root / "Test_motion_113_robot_UPDATED_070725-153342993.txt",

    # "comp-1":    root / "Trace 1-Stable target baseline_robot_300s_UPDATED_070725-125834249.txt",
    # "nc-1":      root / "Trace 1-Stable target baseline_robot_300s_UPDATED_070725-130449938.txt",

    # "comp-2":    root / "Trace 2-Persistant excursion_robot_300s_UPDATED_070725-131135191.txt",
    # "nc-2":      root / "Trace 2-Persistant excursion_robot_300s_UPDATED_070725-132427659.txt",

    # "comp-3":    root / "Trace 3-Erratic behaviour_robot_300s_UPDATED_070725-133018648.txt",
    # "nc-3":      root / "Trace 3-Erratic behaviour_robot_300s_UPDATED_070725-133608424.txt",
    
    # "comp-4":    root / "Trace 4-Continuous target drift_robot_300s_UPDATED_070725-134211669.txt",
    # "nc-4":      root / "Trace 4-Continuous target drift_robot_300s_UPDATED_070725-134754267.txt",

    # "test" : root/"Lung_Baseline_Shifts_AP_120s_robot_UPDATED_220725-164402633.txt"
    }
key  = "test" # <-- change this one line
filepath = files[key]
robot = pd.read_csv(filepath)

# Extraction of the time in ddMMyy_HHmmssfff, conversion from string to float
robot['Time_float'] = robot['Time(ddMMyy_HHmmssfff_format)'].str.split('_').str[1].astype(float)
camera['Time_float'] = camera['Time(ddMMyy_HHmmssfff_format)'].str.split('_').str[1].astype(float)

# Conversion of ddMMyy_HHmmssfff to seconds
def timefloat_to_seconds(t):
    # Convert float or int to zero-padded string of length 9 (HHmmssfff)
    s = f"{int(t):09d}"  # e.g. 125838275 -> "125838275"
    
    HH = int(s[0:2])
    mm = int(s[2:4])
    ss = int(s[4:6])
    fff = int(s[6:9])
    
    total_seconds = HH * 3600 + mm * 60 + ss + fff / 1000
    return total_seconds

camera['Seconds'] = camera['Time_float'].apply(timefloat_to_seconds)
robot['Seconds'] = robot['Time_float'].apply(timefloat_to_seconds)

# Matching of timestamps
# Get the first timestamp of the robot (robot starts moving)
robot_start = robot['Seconds'].iloc[0]

robot['Time_aligned'] = robot['Seconds'] - robot_start
camera['Time_aligned'] = camera['Seconds'] - robot_start 

# Plot the two files
plt.figure(figsize=(17, 8))
plt.plot(camera["Time_aligned"], camera["Distance 1"], label='not compensated motion', color='blue')
plt.plot(robot["Time_aligned"], robot["y(mm)"], label='robot\'s motion', color='black')
plt.xlabel("Time (s)", fontsize=20)
plt.ylabel("Motion (mm)", fontsize=20)
plt.title(BASE_NAME, fontsize=24)
plt.grid(True)
plt.legend(fontsize=20)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.tight_layout()


# Saving as a .png
# result_folder = 'C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Experiments/No_5_final/Results_bis'  
# os.makedirs(result_folder, exist_ok=True)            

# results_png = os.path.join(result_folder, f"{BASE_NAME}.png")

# plt.savefig(results_png)

plt.show()