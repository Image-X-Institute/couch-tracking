# This file creates artificial sinusoidal input motion traces for the 6 DOF robotic arm 
# period range: 3 s to 8 s, peak-to-peak amplitude: 1.5 cm
# The file has 7 columns, only the y columns contains motion = SI direction
# [ Timestamp (0.2 step) , x (mm), y (mm), z (mm), rx (deg), ry (deg), rz (deg)]

import os
import numpy as np
import matplotlib.pyplot as plt

output_folder = r"C:\Users\imagex_labl\Documents\Elisa\Experiments\sinusoidal_traces"
os.makedirs(output_folder, exist_ok = True)

files = [['sin_3.txt', 3], ['sin_5.txt', 5], ['sin_8.txt', 8], ['sin_13.txt', 13]]
signal_length = 60      # in seconds
A = 15                  # mm

for item in files:
    y = []
    t = []
    file_pattern = os.path.join(output_folder, item[0])
    filename = item[0]
    for i in np.arange(0, signal_length+0.2, 0.2):
        data = A * np.sin(2*np.pi*(1/item[1])*i)
        y.append(data)
        t.append(round(i,5))

    with open(file_pattern, "w") as f:
        for ti, yi in zip(t, y):
            f.write(f"{ti:.2f} 0 {yi:.3f} 0 0 0 0\n") 
    print(f"{filename} saved here {output_folder}")    


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