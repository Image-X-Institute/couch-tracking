<img width="1111" alt="Screenshot 2024-11-27 at 10 51 56 am" src="https://github.com/user-attachments/assets/c3933637-0069-4603-927b-0ddaebdeab9f">

The emulator is aim to simulate the couch tracking hardware and algorithm all or partially on software level. The emulator architecture and logic is identical with the real system. Some architecture needed to be adjusted due to programming language change. 


# Emulator -- Motion simulation
<img width="1472" height="749" alt="Screenshot 2025-08-18 at 10 43 42 pm" src="https://github.com/user-attachments/assets/c61150ac-8de5-49fa-aeb9-5835ddb26c85" />


In real world setup, couch tracking is made of two major components: 1) Target tracking, 2) Couch compensation. Two components are communicated via UDP. 

Target tracking is achieved by depth camera that meausures 1D distances, or KIM algorithm that calculates the implanted marker positions from reconstructed kV images in real-time. The tracking tool measures target (patient's internal tumour) motion and send them via UDP in real-time to couch that controlled by Raspberry Pi. Based on the sent measurements, Couch tracking algorithm calculated the deviation of the target from the set iso-centre, and perform motion compensation.

The emulator code integrated_emulator.py takes in a clinical measured patient motion trace, sends out the measurements based on the desired time stamps. At the same time, it receives feedback from couch compensation component. Combined motion represent the true movement of the tracking target that being compensated. At the end of the simulation, the code plots the compensated motion versus orignal input motion which allows us to study the impact of system latency.

- The emulator is able to operate in two modes:
1. Local environment

Data points are transferred via UDP on localhost channel. Couch operation is simulated on local device in Python code. No cross-device UDP communication is needed. 

2. Cross device 

Couch compensation simulation is done on c++, on Raspberry Pi. Tracking data point is read and processed by integrated_emulator.py, and sent on pre-set UDP channel via physical eternet connections. 

- Other features:

1. Latency
2. Motor speed
3. Tracking frequency
4. Target tracking frequency




# Couch compensation
If you would like to run a simulation that cloest to the real-world hardware and software design, an option of running the motion compensation on Raspberry Pi with c++ code is available. The emulator_couch.cpp has the same architecture compared to the real compensation algorithm, apart from the motor is not moving. The moving duration is calculated on moving displacement/motor speed. 

# How to run
python integrated_emulator.py --mode local --trace "Lung_Predominantly_Left_Right_robot_120s.txt" --latency 0 --velocity 12 --track-dt 0.05

Run this command line on window command prompt or visual studio code.

## Mode 
The emulator can be ran in two modes: 1) Local simulation, 2) Data sampling and sending only

1) Local simulation

All simulation, including motor compensation is simualted on one local device

2) Data sampling and sending only

The data receiving and motor compensation is simulated on Raspberry Pi. 

Run emulator_couch.cpp on Raspberry Pi. UDP connection needs to be established via router and ethernet cable.

## Motion to be simulated
trace: Give the motion trace file name

## System latency 
latency: Define the system latency

Unit is in second (s).

## Tracking interval (sample frequency)

track-dt: Define the motion sending interval. Unit is in second. The original motion traces were sampled in 200ms. If a different interval is given, motion file will be interploated.

## Other parameters
Other arguments: UDP ip address etc. The emulator runs by default value if otherwise not specified.







