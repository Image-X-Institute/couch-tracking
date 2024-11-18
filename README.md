# Couch tracking and tumour motion compensation
The couch tracking system receives tracking target positional information in real-time, performs 1-dimentional motion compensation in the superior-inferior direction to compensate for the motion of the target. The aim of developing such a system is to improve efficiency and accuracy of beam delivery during radiation therapy. With the flexibility of commmunicating with various radiation therapy systems, and proven feasilibity of installing such a setup in clinical environment, the couch tracking system has potential of providing a universal solution to real-time adaptive radiation therapy. 

The system consists of a 1-dimensional bullet actuator, sliding couch and a Raspberry Pi. Motion platforms are placed on top of the couch which are able to replicate pre-recorded tumour traces. Any real-time tumour motion monitoring system including KIM/Depth camera sends this motion information via UDP transmission to a Raspberry Pi. Code developed in Raspberry Pi was written in C++. It is responsible of receiving UDP signal, extracting the the signal and convert that into the 1D displacement that motor can travel accordingly. Raspberry Pi receives the target motion information and operates the motor to perform motion compensation accordingly.  

To develop and test the motion compensation performance in an non-clinical environment, motion platforms (1-dimentional motion platform and 6 degree-of-freedom robotic arm) and depth camera were used to simulate tracking target motion and real-time positional data point stream. 

Depth camera is used to verify the accuracy of the motor trace. Depth camera is also used to obtain real-time measurement of a target and letting the motor to replicated the measured motion. 

## Getting Started 
### Requirements
- Couch tracking hardware
  1. Bullet actuator (https://www.firgelliauto.com.au/products/bullet-series-50-cal-linear-actuators)
  2. Raspberry Pi Model 4B 8GB RAM with 32GB SD card (https://www.raspberrypi.com/products/raspberry-pi-4-model-b/)
  3. Motor power supply (https://au.rs-online.com/web/p/switching-power-supplies/9163920)
  4. Motor DC drive (https://www.phippselectronics.com/product/bts7960-43a-double-dc-stepper-motor-driver-h-bridge-pwm/?gad_source=1&gclid=EAIaIQobChMIh7eRzd-HiAMV59oWBR3aBBGWEAQYASABEgKMPvD_BwE)
  5. Sliding couch
     Scale down couch is made of PMMA surface and ball bearing. Full size couch is made of PVC. CAD done by Image X Institute. 
  7. Motor holder and couch surface connector
  8. Intel realsense L515, D4315i depth camera
- Motion platform hardware
  https://github.com/Image-X-Institute/IntERAct
  1. Tracking target (flat and non-reflective material for depth measurement. phantom with internal markers for KIM).
  2. Robot connection with couch surface and the phantom.
- UDP communication
  1. Router (For private, fixed IP address and uninterrupted communication bewteen couch and the end that track the moving object.)
  2. Ethernet cable      
- Software
  1. Microsoft Visual Studio 2022
  2. Python 3.7 or above
  3. Realsense 2 library (If running depth camera)
  
## On Raspberry Pi (MOVE TO COUCH TRACKING FOLDER)
### UDP lisener and Motor operation
####  Raspberry Pi compiling-and-running

1. Compile
- g++ -o [executable filename] [filename.cpp(code needed to be compiled)] -Wall -lwiringPi -std=c++14 -pthread

Compile code on console. The executable and the c++ code name need to be specified. Needed libraries should be included.
2. Running
- sudo ./[executable filename]

Run the executable on console


#### bulletConsole_discrete.cpp
Let the motor run to specific position by input the depth information on console.
#### motor_runbytrace.cpp
Asking the trace you would like to read, and let motor run continuously according to the trace given. 
#### UDPreader_discrete.cpp
It listens to UDP signal and move the motor to the given a position accordingly (discrete motion). The UDP sender is written in Python. 
#### UDPreader_trace.cpp
Listens to KIM UDPsender, and extracts 1D information, moves the motor in opposite direction.
#### UDPreader_realtime.cpp
Listen to UDP transmission that contains 1D depth measurement. Motor home position is set to 100mm. Offset value specify the distance bewteen depth camera and tracking object. Motor begins motion compensation with the given offset as home position. Home position and offset values can be changed and adapt to in practice setup.

## UPD sender (MOVE TO COUCH TRACKING FOLDER)
Lidar 515 cemara minimum detect distance is 50mm. Cameras give most accurate measurement results after temperature drift is stable. It is the best to start depth measurement after switching on the camera for 20 minutes. 
#### realsense_depth.py
Pre-requisite for running depth cameras.
#### UDPsend_MultiROI.py
User gets to select two ROIs with cursor on depth camera frame. After two ROIs being selected, depth measurement starts. The measurements are printed on screen on real-time. Depth measurement from ROI 1 will be sent via UDP sender, which is designed to be listened by Raspberry Pi and operate the couch motor. After exit the depth measurement, frame number, time stamp, ROI 1 measurement, ROI 2 measurement will be stored in an excel file. 

## Result Analysis & Motion generation (MOVE TO COUCH TRACKING FOLDER)
#### motor_analysis.ipynb
The code reads UDP log generated by Couch UDP reader, or log generated by depth camera and KIM, calculate mean and other evaluation metric for comparing uncompensated and compensated motion. The code can also be used to gconvert clinical measured patient motion to trace that follows the format of 1D motion platform and 6DoF robotic arm. 
## Documentation

## Publication

## Future work

## Authors
Ann Yan, Dr. Chandrima Sengupta, Prof. Paul Keall

## Contact
ann.yan@sydney.edu.au

chandrima.sengupta@sydney.edu.au

paul.keall@sydney.edu.au

## Acknowledgements
