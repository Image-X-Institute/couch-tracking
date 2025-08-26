# This code 
# - runs the emulator for sets of 3 parameters
# - save the plot
# - compute the proportion of data under 1 mm (prostate)/ 2mm (lung and liver)
import argparse
import os
import time
import numpy as np
from integrated_emulator import run_emulator

# --- Traces
base_path = r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_6_latency\step_traces"
# traces = {
#     "liver": [os.path.join(base_path, f) for f in [
#         "2.Medium_complexity_093.txt",
#         # "4.Mean_motion_2_111.txt",
#         # "Test_motion_091.txt",
#         "Test_motion_113.txt"]],

#     "lung": [os.path.join(base_path, f) for f in [
#         "Lung_Baseline_Shifts_AP.txt",
#         "Lung_Typical_SI.txt"]],

#     "prostate": [os.path.join(base_path, f) for f in [
#         "Trace 1-Stable target baseline.txt",
#         "Trace 2-Persistant excursion.txt"]]
#         # "Trace 3-Erratic behaviour.txt",
#         # "Trace 4-Continuous target drift.txt"]]
# }
traces = {
    "step": [os.path.join(base_path, f) for f in ["step_3.txt", "step_5.txt", "step_7.txt" ]]
}

# --- Parameters
latency = [0]   # in seconds
motor_speed = [12] # in mm/s
tracking_interval = [0.033] # in seconds


# --- Prepare summary file
summary_file = os.path.join(r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_7_emulator\integrated emulator",f"summary_results_{time.strftime('%Y%m%d_%H%M%S')}.txt")

with open(summary_file, "w") as f:
    f.write("Trace\tType\tLatency(s)\tVelocity(mm/s)\tTrack_dt(s)\tProp_under_tol\n")

# --- Grid search
for type, type_traces in traces.items():
    for trace in type_traces:
        for lat in latency:
            for speed in motor_speed:
                for dt in tracking_interval:
                    args = argparse.Namespace(
                        trace=trace,
                        latency=lat,
                        velocity=speed,
                        track_dt=dt,
                        mode="local",
                        local_port=2400,
                        target_port=1400,
                        pi_ip="192.168.8.2"
                    )
                    sim = run_emulator(args)

                    # --- calculate proportion under tolerance
                    comp = np.abs(sim.compensated)
                    tol = 1.0 if type == "prostate" else 2.0
                    prop_under_tol = np.mean(np.array(comp) <= tol)

                    # --- append to summary file
                    with open(summary_file, "a") as f:
                        f.write(f"{os.path.basename(trace)}\t{type}\t{lat}\t{speed}\t{dt}\t{prop_under_tol:.2%}\n")

print(f"Summary saved to {summary_file}")