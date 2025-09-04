# This scrips plot the diagram for step traces'latency
# It shows the motion of the target (=step trace) and the corresponding motion of 
# the couch with vertical lines to show how the latency has been computed

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

########## DEPTH CAMERA DATA files
ROOT = Path(r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_6_latency\compensation\camera")
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
KEY ="step_3-1" # <-- change this one line
FILEPATH = FILES[KEY]
camera = pd.read_csv(FILEPATH)
BASE_NAME = os.path.splitext(os.path.basename(FILEPATH))[0] # to get the file name for plot title

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
key  = "step_3-1" # <-- change this one line
filepath = files[key]
robot = pd.read_csv(filepath, sep=' ')

##### Timestamps alignement
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

robot['Time_sec']= robot['Time(ddMMyy_HHmmssfff_format)'].str.split('_').str[1].astype(float).apply(timefloat_to_seconds)
robot['Time_sec'] = robot['Time_sec'] - start

# pd.set_option('display.float_format', '{:.0f}'.format)
# subset = camera[(camera["Time_sec"] >= 6) & (camera["Time_sec"] <= 7)]
# print(subset)

####### Plot
fig, ax = plt.subplots(figsize=(12, 8))  # Create fig and ax properly
ax.axhline(0, color='gray', linewidth=0.5, zorder=1)
ax.plot(camera["Time_sec"], -camera["Distance 1"], label='Residual motion', color='orange')
ax.plot(camera["Time_sec"], -camera["Distance 2"], label="Couch", color='black')
ax.plot(robot['Time_sec'], robot["y(mm)"], label="Target", color="green")
text = []

######## STEP 3-1 ############
x_pos = 6.306          # robot
x_pos2 = 6.851          # couch

ax.axvline(x=x_pos, color='red', linestyle='--', linewidth=2)
txt1 = ax.text(5, 3, f"{x_pos:.3f}s", rotation=0, color='red', fontsize=20)
txt1.set_picker(True)
text.append(txt1)

ax.axvline(x=x_pos2, color='red', linestyle='--', linewidth=2)
txt2 = ax.text(7, -4.77, f"{x_pos2:.3f}s", rotation=0, color='red', fontsize=20)
txt2.set_picker(True)
text.append(txt2)

####### STEP 5-1 ###########
# x_pos = 7.664        # robot
# x_pos2 = 8.534       # couch

# ax.axvline(x=x_pos, color='red', linestyle='--', linewidth=2)
# txt1 = ax.text(5, 3, f"{x_pos:.3f}s", rotation=0, color='red', fontsize=20)
# txt1.set_picker(True)
# text.append(txt1)

# ax.axvline(x=x_pos2, color='red', linestyle='--', linewidth=2)
# txt2 = ax.text(7, -4.77, f"{x_pos2:.3f}s", rotation=0, color='red', fontsize=20)
# txt2.set_picker(True)
# text.append(txt2)

######## STEP 7-1 ############
# x_pos = 6.557           # robot
# x_pos2 = 7.572          # couch

# ax.axvline(x=x_pos, color='red', linestyle='--', linewidth=2)
# txt1 = ax.text(4.20, 7.14, f"{x_pos:.3f}s", rotation=0, color='red', fontsize=20)
# txt1.set_picker(True)
# text.append(txt1)

# ax.axvline(x=x_pos2, color='red', linestyle='--', linewidth=2)
# txt2 = ax.text(8.18, -8.71, f"{x_pos2:.3f}s", rotation=0, color='red', fontsize=20)
# txt2.set_picker(True)
# text.append(txt2)

##### Labels and formatting
ax.set_xlabel("Time (s)", fontsize=20)
ax.set_ylabel("Motion (mm)", fontsize=20)
# ax.set_title(BASE_NAME, fontsize=24)
# ax.grid(True)
leg = ax.legend(fontsize=22)
leg.set_draggable(True)  
ax.tick_params(axis='both', labelsize=20)
fig.tight_layout()


# # Saving as a .png
# # result_folder = 'C:/Users/imagex_labl/Documents/GitHub/1D-robot-applications/Elisa/Experiments/No_5_final/Results_bis'  
# # os.makedirs(result_folder, exist_ok=True)            

# # results_png = os.path.join(result_folder, f"{BASE_NAME}.png")

# # plt.savefig(results_png)
selected_text = {'obj': None}

def on_pick(event):
    if isinstance(event.artist, plt.Text):
        selected_text['obj'] = event.artist

def on_motion(event):
    if selected_text['obj'] is not None and event.inaxes == ax:
        selected_text['obj'].set_position((event.xdata, event.ydata))
        fig.canvas.draw()

def on_release(event):
    selected_text['obj'] = None

fig.canvas.mpl_connect('pick_event', on_pick)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)
plt.show()