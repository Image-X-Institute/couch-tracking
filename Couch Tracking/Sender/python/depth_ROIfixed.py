import cv2
import numpy as np
import time
import pandas as pd
from realsense_depth import DepthCamera
 
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
 
# Initialize depth camera
dc = DepthCamera()
 
# Set up mouse callback for selecting ROI
cv2.namedWindow("Color frame")
cv2.setMouseCallback("Color frame", show_distance)
 

dist_array = []
time_array = []
count = 0
start_time = time.time()

while True:
    # Get depth and color frames from the depth camera
    ret, depth_frame, color_frame = dc.get_frame()
 
    # Draw ROI on color frame if selected
    if roi_selected:
        x, y, w, h = roi
        cv2.rectangle(color_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
 
        # Calculate depth measurement for ROI
        distance = get_average_distance(roi, depth_frame)
        elapsed_time = time.time() - start_time
        time_array.append(elapsed_time)
        count += 1
        #  =================== For Realsense L515 model ======================
        distance = distance/4
        # ==================== For D415 model, please silent the above code =======================
        # For Realsense D415 model 
        dist_array.append(distance)
 
        # Print depth measurement on color frame
        cv2.putText(color_frame, f"Distance: {distance:.2f} mm", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
 
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