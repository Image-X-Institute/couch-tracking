# Couch tracking and tumour motion replication 
This project required Raspberry Pi and 1D motor. The motor is receiving tumour positional information via UDP from KIM and generate 1D corresponding motion in real-time.

KIM is responsible for obtaining tumour motions, and send the 3D information via UDP sender. The KIM and UDP sender relevant codes can be found in KIM project. 
Code developed in Raspberry Pi was written in C++. It is responsible of receiving UDP signal, extracting the the signal and convert that into the 1D displacement that motor can travel accordingly. The motor operation code was developed from the previous 1D bullet-actuator application. 
Depth camera is used to verify the accuracy of the motor trace. Depth camera is also used to obtain real-time measurement of a target and letting the motor to replicated the measured motion. 

## On Raspberry Pi
### UDP lisener and Motor operation
####  Raspberry Pi compiling-and-running

1. Complie
- g++ -o [filename] [filename.cpp] -Wall -lwiringPi -std=c++14 -pthread
2. Running
- sudo ./[filename]


#### bulletConsole_discrete.cpp
Let the motor run to specific position by input the depth information on console. The code can be used for testing the motor functionality for debugging purpose.
#### motor_runbytrace.cpp
Asking the trace you would like to read, and let motor run continuously according to the trace given. 
#### UDPreader_discrete.cpp
It listens to UDP signal and move the motor to the given a position accordingly (discrete motion). The UDP sender is written in Python. The code is used for testing the UDP transmission and whether motor can comprehend the incoming data point and execute accordingly.
#### UDPreader_trace.cpp
Listens to KIM UDPsender, and extracts 1D information, moves the motor in opposite direction.
#### UDPreader_realtime_2.cpp
Listen to UDP transmission that contains 1D depth measurement. Motor home position is set to 50mm. Offset value specify the distance bewteen depth camera and tracking object. Motor begins motion compensation with the given offset as home position. Home position and offset values can be changed and adapt to in practice setup. UDP listening and motor motion are seperated into two threads. Motor only execute the latest coming data point and ignore others while it is in operation.
#### UDPread_KIMnoMotion.cpp
Listening to the KIM UDP sender and print the received data point on console. 
#### UDPreader_KIMreplicating.cpp
Listening to the KIM UDP sender and motor replicating 1D motion. The dimensional of the motion that replicated by motor can be specified. This is for testing in-lab, to see if motor is able to comprehend in-coming data point. 
#### UDPreader_KIM.cpp
Listening to KIM UDP sender and perform motion compensation. This is meant to use in clincial environment. Robotic arm is on top of the couch holding a phantom. KV images are collected and processed by KIM. The real-time positional data points are sent via UDP transmission, received by Raspberry Pi which operate the motor to perform motion compensation. 
## UPD sender 
Lidar 515 cemara minimum detect distance is 50mm. Cameras give most accurate measurement results after temperature drift is stable. It is the best to start depth measurement after switching on the camera for 20 minutes. 
#### realsense_depth.py
Pre-requisite for running depth cameras.
#### UDPsend_MultiROI.py
User gets to select two ROIs with cursor on depth camera frame. After two ROIs being selected, depth measurement starts. The measurements are printed on screen on real-time. Depth measurement from ROI 1 will be sent via UDP sender, which is designed to be listened by Raspberry Pi and operate the couch motor. After exit the depth measurement, frame number, time stamp, ROI 1 measurement, ROI 2 measurement will be stored in an excel file. 
#### Other software
The couch tracking system works with both real-time depth camera measurements, and KIM measurements. In clinical setup, KV images are acquired and being processed by KIM, and communicates with couch tracking system via UDP. UDP transmission is built with a physical router and ethernet cables. (UDP can be done wirelessly howvever with the consideration of hospital IT system security requirement and stabilty, we decide to build physical connection.)
#### motor_analysis.ipynb
The code is for motion compensation performance evaluation, 1D platform and 6DoF robotic arm trace generation.
