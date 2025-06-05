<img width="1111" alt="Screenshot 2024-11-27 at 10 51 56 am" src="https://github.com/user-attachments/assets/c3933637-0069-4603-927b-0ddaebdeab9f">

The emulator is aim to simulate the couch tracking hardware and algorithm all on software level. The main structure is identical with the real system. 

## Couch compensation
emulator_couch.cpp run on Raspberry Pi has the identical motion compensation logic compared to the real couch tracking system. As the target tracking component is simulated in emulator, apart from the compensation algorithm, the code also send the couch motor movement to the corresponding device via UDP as feedback.
## Tracking tracking
In real system, target tracking is achieved by depth camera or KIM. The tracking tool measures target motion and send positional information in real-time to couch that controlled by Raspberry Pi. The measurements reflect the tracking target's own movement and couch compensated positions.
In emulator, this is achieved by emulatorSend.ipynb. The code takes in a clinical measured patient motion trace, sends out the measurements based on the orignal time stamps. At the same time, it receives feedback from couch compensation component. Combined motion represent the true movement of the tracking target that being compensated. 
At the end of the simulation, the code plots the compensated motion versus orignal input motion which allows us to study the impact of system latency.
