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
        val = struct.pack('<Q', value)  # Little-endian byte order
 
        # Construct the byte array to send over UDP
        byteArray = b't' + val
 
        # Pad the byte array with zeros to make it 9 bytes long
        byteArray += b'\x00' * (9 - len(byteArray))
 
        return byteArray

    def send_to_udp_KIM(self, gantry, x, y, z):
        message = f"x = {x}, y = {y}, z = {z}, gantry = {gantry}"        
        self.sock.sendto(message.encode(), (self.ip, self.port))         
        print(message)
    
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
# Change the ROI area here
def show_distance(event, x, y, args, params):
    global roi, roi_selected
    if event == cv2.EVENT_LBUTTONDOWN:
        roi = (x, y, 30, 30)
        roi_selected = True
 
roi = ()  # ROI coordinates
roi_selected = False  # Flag to indicate if ROI is selected
 



# Initialize UDP sender
udp_sender = UDP_Communication("172.20.10.2", 1400)  # Change IP and port accordingly
 
# Initialize depth camera
dc = DepthCamera()
 
# Set up mouse callback for selecting point
cv2.namedWindow("Colour frame")
cv2.setMouseCallback("Colour frame", show_distance)

start_time = time.time()
time_interval = 0.1 # 10Hz frame rate
initial_time = start_time
dist_array = []
time_array = []
count = 0


while True:
    # Get depth and color frames from the depth camera
    ret, depth_frame, color_frame = dc.get_frame()
     # Draw ROI on color frame if selected
    if roi_selected:
        x, y, w, h = roi
        cv2.rectangle(color_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Check the current time
        current_time = time.time()
        # Check if the time intervel has elapsed
        if current_time - start_time >= time_interval:

            # Calculate depth measurement for ROI
            distance = get_average_distance(roi, depth_frame)
            #  =================== For Realsense L515 model ======================
            distance = distance/4
            # ==================== For D415 model, please silent the above code =======================
            # Print depth measurement on color frame
            cv2.putText(color_frame, f"Distance: {distance:.2f} mm", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            dist_array.append(distance)
            # Send the distance data over UDP
            udp_sender.send_to_udp(distance)
            
            time_stamp = current_time - initial_time
            time_array.append(time_stamp) 
            # Update the start time with the time spent sleeping
            start_time += time_interval 
        else:
            # Sleep for the remaining time in the interval
            time.sleep(start_time + time_interval - current_time)

        
 


   # Display the color frame
    cv2.imshow("Color frame", color_frame)
 
    key = cv2.waitKey(1)
 
    # Break the loop if 'esc' key is pressed
    if key == 27:
        break
 

# Save the measurements to a CSV file along with timestamps
data_to_save = np.column_stack((time_array, dist_array)) 
np.savetxt('point_measurement.csv', data_to_save, delimiter=',', header='Time,Distance', comments='')
# Release resources
cv2.destroyAllWindows()