import cv2
import numpy as np
import socket
import struct
import time
from datetime import datetime, timezone
from realsense_depth import DepthCamera

# UDP Communication class
class UDP_Communication:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 
    def connect(self):
        return True  # No need for explicit connection in UDP
 
    def convert_depth_to_bytes(self, depth):
        # Convert depth value to 64-bit unsigned integer (UInt64 in C#)
        
        value = int(depth * 100)
        #value = depth*100
        val = struct.pack('<Q', value)  # Little-endian byte order
 
        # Construct the byte array to send over UDP
        byteArray = b't' + val
 
        # Pad the byte array with zeros to make it 9 bytes long
        #byteArray += b'\x00' * (9 - len(byteArray))
 
        return byteArray
    
    def convert_distance_to_bytes(self, distance):
        value = distance*100
        # Convert positional information to 32-bit float
        val = struct.pack('<f', value) # Little-endian byte order
        
        # Construct the byte array to send over UDP
        byteArray = b't' + val
 
        # Pad the byte array with zeros to make it 9 bytes long
        #byteArray += b'\x00' * (9 - len(byteArray))
 
        return byteArray
    '''
    def convert_count_to_bytes(self, count):
        # Convert count value to 32-bit unsigned integer (UInt32 in C#)
        val = struct.pack('<I', count)  # Little-endian byte order
 
        # Construct the byte array to send over UDP
        byteArray = b'c' + val
 
        # Pad the byte array with zeros to make it 6 bytes long
        #byteArray += b'\x00' * (6 - len(byteArray))
 
        return byteArray
    '''
    def convert_count_to_bytes(self, count):
       
       # Convert count value to 32-bit float 
       val = struct.pack('<f', count)  # Little-endian byte order
       byteArray = b'c' + val
       return byteArray
 
    def send_to_udp(self, count, x):
        #formatted_distance = "{:.3f}".format(x)
        message = f"Count = {count}, x = {x}"
        byte_depth = self.convert_distance_to_bytes(x)
        byte_count = self.convert_count_to_bytes(count)
        self.sock.sendto(byte_count + byte_depth, (self.ip, self.port))
        #print(byte_count+byte_depth)
'''
    def send_to_udp(self, x):
        formatted_distance = "{:.3f}".format(x)
        message = f"x = {formatted_distance}"
        byte_depth = self.convert_depth_to_bytes(x)
        self.sock.sendto(byte_depth, (self.ip, self.port))
        print(message)
''' 
# Function to get average distance from a specified ROI in the depth frame
def get_average_distance(roi, depth_frame):
    x, y, w, h = roi
    roi_depth = depth_frame[y:y+h, x:x+w]
    if np.isnan(roi_depth).any():
        return 0  # Return a default value when encountering NaN
    else:
        return np.mean(roi_depth)
 
# Mouse event to specify the points for two ROIs
def show_distance(event, x, y, args, params):
    global points, roi_selected
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 2:
            points.append((x, y))
            if len(points) == 2:
                roi_selected = True
 
points = []  # List to store selected points for two ROIs
roi_selected = False  # Flag to indicate if two ROIs are selected
 
# Initialize UDP sender
udp_sender = UDP_Communication("192.168.8.141", 1400)  # Change IP and port accordingly
 
# Initialize depth camera
dc = DepthCamera()
 
# Set up mouse callback for selecting ROI
cv2.namedWindow("Color frame")
cv2.setMouseCallback("Color frame", show_distance)
 
# Initialize variables
roi = ()  # ROI coordinates
roi_selected = False  # Flag to indicate if ROI is selected

dist_array_1 = [] # Store depth measurements from ROI 1
dist_array_2 = [] # Store depth measurements from ROI 2
time_array = []
time_local_array = []
frame_array = []
frame_number = 0
count = 0

dist_1_multi = []
dist_2_multi = []
start_time = time.perf_counter()

# KIM time interval is 350ms
# Decide time interval that depth measurement is averaged from
frequency_to_mimic = 10 # desired frequncy, e.g. KIM is 10Hz
interval = 1.0/frequency_to_mimic

while True:
    # Loop start time
    loop_start_time = time.perf_counter()
    # Get depth frame from the depth camera
    ret, depth_frame, color_frame, timestamp = dc.get_frame()

    # Draw rectangles for selected ROIs if two ROIs are selected
    img = color_frame.copy()
    if roi_selected:
        for i, point in enumerate(points):
            cv2.rectangle(img, point, (point[0] + 40, point[1] + 40), (255, 0, 0), 2)
            cv2.putText(img, f"ROI {i+1}", (point[0], point[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
 
        # Calculate depth measurements for each ROI
        distance1 = get_average_distance((points[0][0], points[0][1], 40, 40), depth_frame)
        distance2 = get_average_distance((points[1][0], points[1][1], 40, 40), depth_frame)
        count += 1
        # For Lidar 515 camera
        distance1 = round(distance1/4,1)
        distance2 = round(distance2/4,1)

        dist_1_multi.append(distance1)
        dist_2_multi.append(distance2)

        # For D415 camera
        #dist_1_multi.append(distance1)
        #dist_2_multi.append(distance2)

        
        # Print distance readings on the screen
        cv2.putText(img, f"ROI 1 Distance: {distance1:.2f} mm", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(img, f"ROI 2 Distance: {distance2:.2f} mm", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)



        elapsed_time = time.perf_counter()-start_time

        if elapsed_time >= interval:
            #d1 = np.mean(dist_1_multi)
            #d2 = np.mean(dist_2_multi)
            #dist_array_1.append(d1)
            #dist_array_2.append(d2)
            frame_number += 1
            frame_array.append(frame_number)
            time_array.append(timestamp)
            # Empty the depth measurement array and later store the new measurements
            #dist_1_multi = []
            #dist_2_multi = []
            # Send only one depth measurement over UDP (for example, send distance1)
            #udp_sender.send_to_udp(frame_number, d1)  # Convert mm to meters
            
            # Timestamp from Unix epoch
            time_local_array.append(time.time())

            # Conversion unix timestamp to Time(ddMMyy_HHmmssfff) format to match robot's timestamp
            time_local_array_dt =  [datetime.fromtimestamp(t) for t in time_local_array]
            time_local_array_dt = [dt.strftime('%d%m%y_%H%M%S') + f"{int(dt.microsecond / 1000):03d}" for dt in time_local_array_dt]

            udp_sender.send_to_udp(frame_number, distance1)
            dist_array_1.append(distance1)
            dist_array_2.append(distance2)
            #print(distance1)
            #time.sleep(time_delay)
 
    # Display the depth frame
    cv2.imshow("Color frame", img)

    # Calculate the time taken for the loop and sleep to maintain consistent frequency
    loop_end_time = time.perf_counter()
    loop_duration = loop_end_time - loop_start_time
    if loop_duration < interval:
        time.sleep(interval-loop_duration)
 
    key = cv2.waitKey(1)
 
    # Break the loop if 'esc' key is pressed
    if key == 27:
        break

# Convert lists to numpy arrays
dist_array_1 = np.array(dist_array_1)
dist_array_2 = np.array(dist_array_2)
frame_array = np.array(frame_array)
time_array = np.array(time_array)
time_local_array = np.array(time_local_array)

# Ensure there are more than 30 frames
if len(dist_array_1) > 30:
    # Calculate isocenter positions (mean of first 30 frames)
    home_1 = np.mean(dist_array_1[:30])
    home_2 = np.mean(dist_array_2[:30])

    # Subtract home position from all subsequent frames
    dist_array_1 = dist_array_1[30:] - home_1
    dist_array_2 = dist_array_2[30:] - home_2
    frame_array = frame_array[30:]
    time_array = time_array[30:]
    time_local_array = time_local_array[30:]
    time_local_array_dt = time_local_array_dt[30:]

    # Stack and save to CSV
    data_to_save = np.column_stack((frame_array,time_array,time_local_array_dt,dist_array_1,dist_array_2)).astype(str)
    save_path = r"C:\Users\imagex_labl\Documents\GitHub\1D-couch-applications\Elisa\Experiments\No_5_final\Test_motion_113_robot_UPDATED_nc.csv"  
    np.savetxt(save_path, data_to_save, delimiter=',', 
               header='Count,Time,Time(ddMMyy_HHmmssfff_format),Distance 1,Distance 2', comments='', fmt='%s')
    print("Data saved with home compensation applied.")
else:
    print("Not enough frames collected to compute home position (need > 30). No CSV saved.")

cv2.destroyAllWindows()
