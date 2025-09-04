# This file creates artificial step input motion traces for the 6 DOF robotic arm 
# step amplitude: 5 mm, 10 mm, 15 mm, period = 
# The file has 7 columns, only the y columns contains motion = SI direction
# [ Timestamp (0.2 step) , x (mm), y (mm), z (mm), rx (deg), ry (deg), rz (deg)]

import os
import numpy as np
import matplotlib.pyplot as plt

output_folder = r"C:\Users\imagex_labl\Documents\Elisa\Experiments\step_traces"
os.makedirs(output_folder, exist_ok = True)

files = [['step_5.txt', 5], ['step_3.txt', 3], ['step_7.txt', 7]]
num_steps = 4            
step_duration = 10
pause = 5

signal_length = num_steps*(step_duration + pause) + pause

t = np.arange(0, signal_length+0.2, 0.2)


for item in files:
    y = np.zeros_like(t)
    file_pattern = os.path.join(output_folder, item[0])
    filename = item[0]
    start = 0
    for j in range(1,num_steps+1):
        start = j*pause + step_duration*(j-1)
        end = j*pause + step_duration*j
        # print(end)
        y[(t >= start) & (t < end)] = item[1]
        
    with open(file_pattern, "w") as f:
        for ti, yi in zip(t, y):
            f.write(f"{ti:.2f} 0 {yi:.3f} 0 0 0 0\n") 
    print(f"{filename} saved here {output_folder}")    


# Plot it
plt.plot(t, y, drawstyle='steps-post')
plt.xlabel('Time (s)')
plt.ylabel('Step Value')
plt.title('3-Step Function over 60 seconds')
plt.grid(True)
plt.show()

# Plot data to check the result
# plt.figure(figsize=(17, 8))
# plt.plot(t, y, label=filename, color='blue')
# plt.xlabel("Time (s)", fontsize=20)
# plt.ylabel("Motion (mm)", fontsize=20)
# plt.title(filename, fontsize=24)
# plt.grid(True)
# plt.legend(fontsize=20)
# plt.xticks(fontsize=20)
# plt.yticks(fontsize=20)
# plt.tight_layout()
# plt.show()