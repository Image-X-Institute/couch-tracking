# Sine wave fitting or depth camera data to determine maximums and compute latency between target motion and couch's response

import numpy as np
import csv
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os
from pathlib import Path
from scipy.signal import find_peaks

########## DEPTH CAMERA DATA files
ROOT = Path(r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_6_latency\replication_load\camera")
FILES = {
    "sin_5-1" : ROOT /"sin_5_repl_load-1.csv",    "sin_5-2" : ROOT /"sin_5_repl_load-2.csv",    "sin_5-3" : ROOT /"sin_5_repl_load-3.csv",
    "sin_8-1" : ROOT /"sin_8_repl_load-1.csv",    "sin_8-2" : ROOT /"sin_8_repl_load-2.csv",    "sin_8-3" : ROOT /"sin_8_repl_load-3.csv",
    "sin_13-1" : ROOT /"sin_13_repl_load-1.csv",  "sin_13-2" : ROOT /"sin_13_repl_load-2.csv",  "sin_13-3" : ROOT /"sin_13_repl_load-3.csv",
    }
KEY = "sin_13-1" # <-- change this one line
FILEPATH = FILES[KEY]
camera = pd.read_csv(FILEPATH)
BASE_NAME = os.path.splitext(os.path.basename(FILEPATH))[0] # to get the file name for plot title

# Convertion of Time() to seconds
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

camera['Time_sec'] = camera['Time(ddMMyy_HHmmssfff_format)'].str.split('_').str[1].astype(float)
camera['Time_sec'] = camera['Time_sec'].apply(timefloat_to_seconds)

start = camera['Time_sec'].iloc[0]
camera['Time_sec'] = camera['Time_sec'] - start

time = camera['Time_sec'] 
distance1 = camera["Distance 1"]
distance2 = camera["Distance 2"]

## Trimming of the data to keep only the central region (remove outliers from camera start/stop)
n = len(time)
trim_fraction = 0.1  # 5% from each end
# save = 1

# Initial guess: A, f, phi, C
guess = [15, 1/13, 0, 0]
guess2 = [15, 1/13, 0, 0]

start_idx = int(n * trim_fraction)
end_idx = int(n * (1 - trim_fraction))

# Keep only central region
t_trimmed = time[start_idx:end_idx]
distance1_trimmed = distance1[start_idx:end_idx]
distance2_trimmed = distance2[start_idx:end_idx]

# Define sine function to fit
def sine_func(t, A, f, phi, C):
    return A * np.sin(2 * np.pi * f * t + phi) + C

# Fit the data
params1, _ = curve_fit(sine_func, t_trimmed, distance1_trimmed, p0=guess)  # find the best parameters for amplitude, frequency, phase and offset
params2, _ = curve_fit(sine_func, t_trimmed, distance2_trimmed, p0=guess2)

# Extract fitted parameters
A_fit1, f_fit1, phi_fit1, C_fit1 = params1
max_amplitude1 = abs(A_fit1)

A_fit2, f_fit2, phi_fit2, C_fit2 = params2
max_amplitude2 = abs(A_fit2)

# print(f"Amplitude: {max_amplitude1:.3f}, Frequency: {f_fit1:.3f} Hz")
# print(f"Amplitude: {max_amplitude2:.3f}, Frequency: {f_fit2:.3f} Hz")

# Plot data and fitted curve
t_fit = np.linspace(min(t_trimmed), max(t_trimmed), 1000)
distance1_fit = sine_func(t_fit, *params1)
distance2_fit = sine_func(t_fit, *params2)

## Find peaks for Distance 1
peak_indices1, _ = find_peaks(distance1_fit, prominence = 0.5)  # adjust 'prominence' as needed
peak_times1 = t_fit[peak_indices1]
peak_values1 = distance1_fit[peak_indices1]

## Find peaks for Distance 2
peak_indices2, _ = find_peaks(distance2_fit, prominence = 0.1)  # adjust 'prominence' as needed
peak_times2 = t_fit[peak_indices2]
peak_values2 = distance2_fit[peak_indices2]

# Print the results
# print("Distance 1")
# for time_val, peak_val in zip(peak_times1, peak_values1):
#     print(f"Time: {time_val:.3f}, Peak: {peak_val:.3f}")

# print("Distance 2")
# for time_val, peak_val in zip(peak_times2, peak_values2):
#     print(f"Time: {time_val:.3f}, Peak: {peak_val:.3f}")

# Compute latency
latency = [(t2 - t1)* 1e3 for t1, t2 in zip(peak_times1, peak_times2)]

# Save to csv
# folder = r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_6_latency\compensation"
# csv_file = os.path.join(folder, f"{BASE_NAME}_peaks.csv")

# Determine number of peaks (ensure equal length for both traces)
n_peaks = max(len(peak_times1), len(peak_times2))

# Pad shorter lists with empty strings if needed
def pad_list(lst, target_len):
    return lst + [''] * (target_len - len(lst))

pt1_list = pad_list([f"{pt:.3f}" for pt in peak_times1], n_peaks)
pv1_list = pad_list([f"{pv:.3f}" for pv in peak_values1], n_peaks)
pt2_list = pad_list([f"{pt:.3f}" for pt in peak_times2], n_peaks)
pv2_list = pad_list([f"{pv:.3f}" for pv in peak_values2], n_peaks)
latency_list = pad_list(latency, n_peaks)

df = pd.DataFrame({
    "Peaks Time D1 (s)": pt1_list,
    "Peaks Value D1 (mm)": pv1_list,
    "Peaks Time D2 (s)": pt2_list,
    "Peaks Value D2 (mm)": pv2_list,
    "Latency (ms)" : latency_list,
})

# df.to_csv(csv_file, mode='w', header=True, index=False)
# print(f"Run {BASE_NAME} written to {csv_file}")


# Plot data
fig, ax = plt.subplots(figsize=(12, 8))

ax.plot(time, distance1, linestyle='--', color='red', label='Target')
ax.plot(time, distance2, linestyle='--', color='green', label='Replicating Couch')
ax.axhline(0, color='gray', linewidth=0.5, zorder=1)
ax.plot(peak_times1, peak_values1, 'ro', label="Target's Peaks")
ax.plot(peak_times2, peak_values2, 'go', label="Couch's Peaks")
# ax.plot(t_fit, distance1_fit, 'r-', label='Fitted Target Sine Wave')
# ax.plot(t_fit, distance2_fit, 'g-', label='Fitted Couch Sine Wave')

# Vertical lines + text
text = []
if len(peak_times1) >= 3:
    pt = peak_times1[2]
    pv = peak_values1[2]
    ax.axvline(x=pt, color='red', linestyle='-', alpha=0.6)
    txt =ax.text(pt + 1.5, pv, f"{pt:.3f}s", rotation=0, color='red', fontsize=24)
    txt.set_picker(True)
    text.append(txt)

if len(peak_times2) >= 3:
    pt = peak_times2[2]
    pv = peak_values2[2]
    ax.axvline(x=pt, color='green', linestyle='-', alpha=0.6)
    txt2 = ax.text(pt + 1, pv, f"{pt:.3f}s", rotation=0, color='green', fontsize=24)
    txt2.set_picker(True)
    text.append(txt2)

# Labels and layout
# ax.set_title(BASE_NAME, fontsize=28)
ax.set_xlabel("Time (s)", fontsize=20)
ax.set_ylabel("Motion (mm)", fontsize=20)
ax.tick_params(axis='both', labelsize=20)
# ax.grid(True)

legend = ax.legend(fontsize=22, loc='best')
legend.set_draggable(True)

fig.tight_layout()

# Save if needed
# if save:
#     os.makedirs(folder, exist_ok=True)            
#     results_png = os.path.join(folder, f"{BASE_NAME}.png")
#     fig.savefig(results_png)
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