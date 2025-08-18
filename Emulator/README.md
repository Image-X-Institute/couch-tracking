<img width="1111" alt="Screenshot 2024-11-27 at 10 51 56 am" src="https://github.com/user-attachments/assets/c3933637-0069-4603-927b-0ddaebdeab9f">

The emulator is aim to simulate the couch tracking hardware and algorithm all or partially on software level. The emulator architecture and logic is identical with the real system. Some architecture needed to be adjusted due to programming language change. 


# Emulator -- Motion simulation
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




## Couch compensation
emulator_couch.cpp run on Raspberry Pi has the identical motion compensation logic compared to the real couch tracking system. As the target tracking component is simulated in emulator, apart from the compensation algorithm, the code also send the couch motor movement to the corresponding device via UDP as feedback.
