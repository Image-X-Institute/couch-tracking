# This script edit couch log file to have the same structure as files from the depth camera

import numpy as np
import os
import pandas as pd
from datetime import datetime

input_folder = r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_6_Latency\log_files"
output_folder = r"C:\Users\imagex_labl\Documents\Elisa\Experiments\No_6_Latency\log_files"
os.makedirs(output_folder, exist_ok=True)  # create new folder 

# Keep lines with 5 columns
for filename in os.listdir(input_folder):
    cleaned_lines = []
    if filename.endswith(".txt"):
         text_path = os.path.join(input_folder, filename)
         with open(text_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 5:
                    cleaned_lines.append(parts)

    couch = pd.DataFrame(cleaned_lines, columns=['Frame', 'Timestamp', 'Depth', 'Adjusted_position', 'Move'])

    # Convert string to float values
    couch['Adjusted_position'] = pd.to_numeric(couch['Adjusted_position'])

    # Remove the offset = couch's home position = 50 mm
    couch['Adjusted_position'] = couch['Adjusted_position'] - 50  
    # couch_position = couch['Adjusted_position']
    # time = couch['Timestamp']

    ### Convert Unix timestamps in Time(ddMMyy_HHmmssfff_format)    
    # Convert Timestamp column from string to datetime
    couch['Time(dt_obj)'] = couch['Timestamp'].apply(lambda t: datetime.fromtimestamp(float(t) / 1_000_000))

    # Format to ddMMyy_HHmmssfff
    couch['Time(ddMMyy_HHmmssfff_format)'] = couch['Time(dt_obj)'].apply(lambda dt: dt.strftime('%d%m%y_%H%M%S') + f"{int(dt.microsecond / 1000):03d}")

    # Drop the intermediate datetime column
    couch.drop(columns='Time(dt_obj)', inplace=True)

    # Save the edited log file
    output_file = os.path.join(output_folder, filename.replace('.txt', '.csv'))
    couch.to_csv(output_file, index=False, header=True)
    print(f"✔️ {output_file} -> {output_folder}")




