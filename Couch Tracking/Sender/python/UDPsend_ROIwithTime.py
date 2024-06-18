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
 
    def convert_depth_to_bytes(self, depth):
        # Convert depth value to 64-bit unsigned integer (UInt64 in C#)
        value = int(depth * 100)
        val = struct.pack('<Q', value)  # Little-endian byte order
 
        # Construct the byte array to send over UDP
        byteArray = b't' + val
 
        # Pad the byte array with zeros to make it 9 bytes long
        byteArray += b'\x00' * (9 - len(byteArray))
 
        return byteArray
 
    def send_to_udp(self, x):
        formatted_distance = "{:.3f}".format(x)
        message = f"x = {formatted_distance}"
        byte_depth = self.convert_depth_to_bytes(x)
        self.sock.sendto(byte_depth, (self.ip, self.port))
        print(message)
 
# Function to get average distance from a specified ROI in the depth frame
def get_average_distance(roi, depth_frame):
    x, y, w, h = roi
    roi_depth = depth_frame[y:y+h, x:x+w]
    if np.isnan(roi_depth).any():
        return 0  # Return a default value when encountering NaN
    else:
        return np.mean(roi_depth)
 
# Mouse event to specify the ROI
def show_distance(event, x, y, flags, param):
    global roi, roi_selected
    if event == cv2.EVENT_LBUTTONDOWN:
        roi = (x, y, 30, 30)
        roi_selected = True
 
# Initialize UDP sender
udp_sender = UDP_Communication("172.20.10.2", 1400)  # Change IP and port accordingly
 
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
time_delay = 2  # 10Hz frame rate
dist_array = []
time_array = []
count_array = []
count = 0
# Main loop
while True:
    # Get depth and color frames from the depth camera
    ret, depth_frame, color_frame, timestamp = dc.get_frame()
    
    # Draw ROI on color frame if selected
    if roi_selected:
        start_time = time.time() 
        
        
        x, y, w, h = roi
        cv2.rectangle(color_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # Calculate depth measurement for ROI
        distance = get_average_distance(roi, depth_frame)
            
        # Convert depth measurement for Realsense L515 model
        distance = distance / 4
        # Print depth measurement on color frame
        cv2.putText(color_frame, f"Distance: {distance:.2f} mm", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        # Send the distance data over UDP
        udp_sender.send_to_udp(distance)
        dist_array.append(distance)
        count += 1
        count_array.append(count)
        time_array.append(start_time)
        time.sleep(time_delay)

    
    # Display the color frame
    cv2.imshow("Color frame", color_frame)
 
    key = cv2.waitKey(1)
 
    # Break the loop if 'esc' key is pressed
    if key == 27:
        break
 
# Save the measurements to a CSV file along with timestamps
data_to_save = np.column_stack((count_array, time_array, dist_array))
np.savetxt('point_measurement_1.csv', data_to_save, delimiter=',', header='Count,Time,Distance', comments='')
 
# Release resources
cv2.destroyAllWindows()