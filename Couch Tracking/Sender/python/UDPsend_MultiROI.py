import cv2
import numpy as np
import socket
import struct
import time
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
    def convert_count_to_bytes(self, count):
        # Convert count value to 32-bit unsigned integer (UInt32 in C#)
        val = struct.pack('<I', count)  # Little-endian byte order
 
        # Construct the byte array to send over UDP
        byteArray = b'c' + val
 
        # Pad the byte array with zeros to make it 6 bytes long
        #byteArray += b'\x00' * (6 - len(byteArray))
 
        return byteArray
 
    def send_to_udp(self, count, x):
        formatted_distance = "{:.3f}".format(x)
        message = f"Count = {count}, x = {formatted_distance}"
        byte_depth = self.convert_depth_to_bytes(x)
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
udp_sender = UDP_Communication("192.168.8.2", 1400)  # Change IP and port accordingly
 
# Initialize depth camera
dc = DepthCamera()
 
# Set up mouse callback for selecting ROI
cv2.namedWindow("Color frame")
cv2.setMouseCallback("Color frame", show_distance)
 
# Initialize variables
roi = ()  # ROI coordinates
roi_selected = False  # Flag to indicate if ROI is selected
start_time = time.time()
initial_time = start_time
#time_delay = 0.1  # 10Hz frame rate
dist_array_1 = [] # Store depth measurements from ROI 1
dist_array_2 = [] # Store depth measurements from ROI 2
time_array = []
frame_array = []
frame_number = 0
count = 0

dist_1_multi = []
dist_2_multi = []

while True:
    # Get depth frame from the depth camera
    ret, depth_frame, color_frame, timestamp = dc.get_frame()
 
    # Draw rectangles for selected ROIs if two ROIs are selected
    img = color_frame.copy()
    if roi_selected:
        for i, point in enumerate(points):
            cv2.rectangle(img, point, (point[0] + 30, point[1] + 30), (255, 0, 0), 2)
            cv2.putText(img, f"ROI {i+1}", (point[0], point[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
 
        # Calculate depth measurements for each ROI
        distance1 = get_average_distance((points[0][0], points[0][1], 30, 30), depth_frame)
        distance2 = get_average_distance((points[1][0], points[1][1], 30, 30), depth_frame)
        count += 1
        # For Lidar 515 camera
        distance1 = distance1/4
        distance2 = distance2/4

        dist_1_multi.append(distance1)
        dist_2_multi.append(distance2)
        # For D415 camera
        #dist_1_multi.append(distance1)
        #dist_2_multi.append(distance2)

        
        # Print distance readings on the screen
        cv2.putText(img, f"ROI 1 Distance: {distance1:.2f} mm", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(img, f"ROI 2 Distance: {distance2:.2f} mm", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Decide the frame number that depth measurement is averaged from
        if count == 10:
            d1 = np.mean(dist_1_multi)
            d2 = np.mean(dist_2_multi)
            dist_array_1.append(d1)
            dist_array_2.append(d2)
            frame_number += 1
            frame_array.append(frame_number)
            time_array.append(timestamp)
            # Empty the depth measurement array and later store the new measurements
            dist_1_multi = []
            dist_2_multi = []
            count = 0
            # Send only one depth measurement over UDP (for example, send distance1)
            udp_sender.send_to_udp(frame_number, d1)  # Convert mm to meters
            print(d1)
            #time.sleep(time_delay)
 
    # Display the depth frame
    cv2.imshow("Color frame", img)
 
    key = cv2.waitKey(1)
 
    # Break the loop if 'esc' key is pressed
    if key == 27:
        break

# Save the measurements to a CSV file along with timestamps
data_to_save = np.column_stack((frame_array, time_array, dist_array_1, dist_array_2))
np.savetxt('1D_only_sine_2.5s_5mm.csv', data_to_save, delimiter=',', header='Count,Time,Distance 1, Distance 2', comments='')
# Release resources
cv2.destroyAllWindows()
