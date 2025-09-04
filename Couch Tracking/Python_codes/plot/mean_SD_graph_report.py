# This scripts plots a diagramm of the mean deviation for each trace with the standard deviation bars around

import numpy as np
import matplotlib.pyplot as plt

# Trace names
trace_names = [
    "Stable target baseline", "Persistent excursion", "Erratic behaviour", "Continuous target drift",
    "Test motion 091", "Test motion 113", "Medium complexity 093", "Mean motion 2 111",
    "Lung Baseline Shifts AP", "Lung Typical SI"
]
# trace_names = [
#     "Stable target baseline (1)", "Persistent excursion (2)", "Erratic behaviour (3)", "Continuous target drift (4)",
#     "Test motion 091 (5)", "Test motion 113 (6)", "Medium complexity 093 (7)", "Mean motion 2 111 (8)",
#     "Lung Baseline Shifts AP (9)", "Lung Typical SI (10)"
# ]

# trace_names = [
#     "(1)", "(2)", "(3)", "(4)", "(5)", "(6)", "(7)", "(8)", "(9)", "(10)"
# ]

# MAE values (Original, Compensated)
# mae_original = np.round([0.24, 2.9, 1.18, 2.18, 3.5, 9.36, 3.76, 11.46, 2.29, 1.89], 1)
mae_original = np.round([0.24, 3.35, 1.07, 1.48, 2.91, 5.8, 3, 5.51, 2.26, 1.71 ], 1)
mae_comp = np.round([0.55, 0.8, 0.88, 0.65, 1.43, 1.32, 1.7, 1.76, 1.04, 0.94],1)

# Standard deviation values (Original, Compensated)
# std_original = np.round([0.23, 2.88, 0.63, 1.64, 3.31, 6.12, 2.18, 6.22, 1.62, 1.08],1)
std_original = np.round([0.23, 1, 0.66, 0.8, 1.73, 3.24, 2.13, 2.89, 1.64, 1.1],1)
std_comp = np.round([0.45, 0.63, 0.62, 0.54, 1.22, 1.48, 1.59, 1.53, 0.83, 0.74],1)

for i, (mae, std) in enumerate(zip(mae_comp, std_comp)):
    print(f"mae_original({i}) = {mae} ± {std}")

# X positions and offset
x = np.arange(len(trace_names))
offset = 0.15

# Plot "Original" (red circles)
plt.figure(figsize=(9, 8))  # Increase plot size

# Plot "Original" (red circles)
plt.errorbar(x - offset, mae_original, yerr=std_original,
             fmt='^', color='blue', label='Original traces',
             capsize=4)

# Plot "Compensated" (blue triangles)
plt.errorbar(x + offset, mae_comp, yerr=std_comp,
             fmt='o', color='red', label='With compensation',
             capsize=4)

# Labels and formatting
plt.xticks(x, trace_names, rotation=45, ha="right", fontsize=16)
# plt.xticks(x, trace_names, rotation=0, ha="center", fontsize=16)
plt.yticks(fontsize=16)
plt.ylabel("Mean deviation in mm", fontsize=16)
# plt.xlabel("Trace name", fontsize=14)
plt.legend(fontsize=16)
plt.tight_layout()
plt.show()

