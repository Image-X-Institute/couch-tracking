# This script aims to derivate input traces (position as a function of time) to get the speed and the acceleration
# the robot should be able to achieve to compensate
import os
import pandas as pd
import numpy as np
import glob

input_folder = r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_6_latency\step_traces\updated"
output_folder = r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_6_latency\step_traces"
os.makedirs(output_folder, exist_ok=True)  # create new folder 

# Get all the files that end with ".txt"
file_pattern = os.path.join(input_folder, '*.txt')
output_filename = "max_speed_acceleration_step_traces.csv"
results = []
# Save the output in the desired folder
output_file = os.path.join(output_folder, output_filename)

file_paths = glob.glob(file_pattern)
file_paths.sort(key=lambda x: int(os.path.basename(x).split('_')[1].split('.')[0]))

for file_path in file_paths:
    filename = os.path.splitext(os.path.basename(file_path))[0] #.replace('_UPDATED', '') 
    trace = np.loadtxt(file_path)

    # Compute velocity for each traces, and keep the highest one
    time = trace[:,0]
    distance1 = trace[:,2]
    speed = np.gradient(distance1, time)
    acceleration = np.gradient(speed,time)

    # p10 = np.percentile(abs(speed), 10)
    # p90 = np.percentile(abs(speed), 90)

    max_speed = max(abs(speed))
    # mean_speed = np.mean(abs(speed))
    max_acceleration = max(abs(acceleration))
    results.append([filename,round(max_speed, 2), round(max_acceleration, 2)])
    # results.append([filename, round(mean_speed, 2), round(p10, 2),round(p90, 2) ,round(max_speed, 2), round(max_acceleration, 2)])

# Create DataFrame and save
df = pd.DataFrame(results, columns=["Trace", "Max Speed (mm/s)", "Max Acceleration (mm/s**2)"])
# df = pd.DataFrame(results, columns=["Trace", "Mean Speed (mm/s)", "10th percentile speed (mm/s)", "90th percentile speed (mm/s)", "Max Speed (mm/s)", "Max Acceleration (mm/s**2)"])
output_file = os.path.join(output_folder, output_filename)
df.to_csv(output_file, index=False)

print(f"{output_filename} saved here {output_folder}")