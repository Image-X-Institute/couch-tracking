# Couch tracking and tumour motion compensation
The couch tracking system receives tracking target positional information in real-time, performs 1-dimentional motion compensation in the superior-inferior direction to compensate for the motion of the target. The aim of developing such a system is to improve efficiency and accuracy of beam delivery during radiation therapy. With the flexibility of commmunicating with various radiation therapy systems, and proven feasilibity of installing such a setup in clinical environment, the couch tracking system has potential of providing a universal solution to real-time adaptive radiation therapy. 

The system consists of a 1-dimensional bullet actuator, sliding couch and a Raspberry Pi. Motion platforms are placed on top of the couch which are able to replicate pre-recorded tumour traces. Any real-time tumour motion monitoring system including KIM/Depth camera sends this motion information via UDP transmission to the Raspberry Pi. Code developed in Raspberry Pi was written in C++. It is responsible of receiving UDP signal, extracting the the signal and convert that into the 1D displacement that the couch motor should travel to and achieve compensation.   

To develop and test the motion compensation performance in an non-clinical environment, motion platforms (1-dimentional motion platform and 6 degree-of-freedom robotic arm) and depth camera were used to simulate tracking target motion and real-time positional data point stream. 

For the system overview, see Couch tracking flowchart.pptx

<img width="943" alt="Screenshot 2024-11-20 at 12 34 02 pm" src="https://github.com/user-attachments/assets/1993e61a-e578-4d34-b325-3c5e09cbad82">



## HARDWARE 
### Couch
Treatment couch is designated to hold patient meanwhile capable of moving in 1-dimensional direction. Couch contains a base and a sliding top, the base part sits on top of the in-room treatment couch, the sliding part is connected to motor that enable motion compensation in 1D. Couch design and dimension is included in CTCouchDimensions.pptx.
### Linear actuator motor (couch motor)
Motor sits on the upper part of the couch base and connected to the sliding part of the couch. The motor is able to extend or extract at highest speed 12mm/s. A Raspberry Pi operates the couch motor corresponding to real-time tracking target measurement.
### Motion platform
Motion platform is used to simulate patient motion for research and development purpose. In Image X laboratory, a 1-dimensional motion platform or a 6 degree-of-freedom robotic arm replicates real clincial recored patient motion, an item held by the motion platform is tracked in real-time.
### Target tracking tools
- For development purpose, Intel RealSense Lidar 515 camera is used to measure 1D distance between itself to tracking target.
- kV imager Elekta (?)
## SOFTWARE
### Motion compensation algorithm
Motion compensation code is written in C++ and executed by Raspberry Pi (Linux system). Details can be found in Couch tracking folder. Motion compensation algorithm, unit testing code, sample couch running log and results are all included. 
### Motion platform control and input trace
Motion platform control code can be found in Image-X-Institute-IntERAct github repository. 

- 1D motion platform input trace
  Trace contains timestamp and 1D positional information. Timestamps have 0.2 second interval.

- 6DoF robotic arm input trace
  Trace contains timestamp, positional information in AP, SI, LR, rAP, rSI, rLR directions. Timestamps have 0.2 second interval.

Liver, lung and prostate motion trace in 1D motion platform and 6DoF robotic arm format can be found in Motion trace folder. 
### Target tracking methods
- Depth measurement
Details can be found in Couch tracking/Sender.
- Kv imager with KIM algorithm 

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
