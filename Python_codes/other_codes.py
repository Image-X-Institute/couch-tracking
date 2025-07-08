import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set global font to Palatino Linotype
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Palatino Linotype']

# Optional: adjust font size globally
rcParams['font.size'] = 12

# Test plot
plt.plot([1, 2, 3], [1, 4, 9])
plt.title("Plot Title")
plt.xlabel("X Axis")
plt.ylabel("Y Axis")
plt.grid(True)
plt.show()

# # # Just for debugging
# with open(r"C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/debug_output.txt", "w") as f:
#     for val in jumps:
#         f.write(f"{val}\n")      # True / False on separate lines