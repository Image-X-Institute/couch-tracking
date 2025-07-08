# When executed, this file makes a copy of the output files of the Phantom Control appication and removes the extra space in 
# the header that disturbs the splitting of the columns  
import os
import re
import pandas as pd


input_folder = r"C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/IntERAct-Release-v1.5/Release/Output Files/6DPlatform/test"
output_folder = r"C:/Users/imagex_labl/Documents/GitHub/1D-couch-applications/Elisa/Experiments/No_5_final/good_files"
os.makedirs(output_folder, exist_ok=True)  # create new folder 

# browse all .TXT files in the folder
for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        txt_path = os.path.join(input_folder, filename)

        # Reading of the first line to modify the header
        with open(txt_path, 'r') as f:
            header_line = f.readline().strip()

        # Removing of the extra space in the reader
        header_line = header_line.replace("Time(ddMMyy_HHmmssfff format)", "Time(ddMMyy_HHmmssfff_format)")
        headers = header_line.split()

        # Reads the file
        df = pd.read_csv(txt_path, sep=r"\s+", skiprows=1, header=None)
        df.columns = headers

        # Remove the first line of actual data bc it appears twice
        df = df.iloc[1:].reset_index(drop=True)

        #base_filename = re.sub(r'_UPDATED.*', '', filename)
        output_path = os.path.join(output_folder, filename)

        with open(output_path, 'w') as f:
            f.write(','.join(headers) + '\n')
        
        df.to_csv(output_path, sep=',', index=False, header=False, mode ='a')
        print(f"✔️ {filename} -> {output_path}")

