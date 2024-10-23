#include <wiringPi.h>
#include <wiringSerial.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <fstream>
#include <thread>
#include <cmath>
#include <numeric>
#include <chrono>

#include <vector>
#include <algorithm>

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>
#include <cstring>
#include <string.h>
#include <ifaddrs.h>

#include <queue>
#include <mutex>
#include <condition_variable>
#include "logger.cpp"

#define SIZE 512
#define PORT 1400

using namespace std;
using namespace std::chrono;

ofstream logFile; // Global file stream for logging
int RPWM=26; //PWM signal right side
int LPWM=23; 
int _interrupt = 15;

volatile long sensorVal=0; 
volatile int stepsPerMill = 155;

int Speed = 1023; //choose any speed in the range [0, 1023]
double falsepulseDelay = 10; //10us delay
int Direction; //-1 = retracting, 0 = stopped, 1 = extending

long pulseTotal=0; //stores number of pulses in one full extension/actuation
double mean_depth = 0, current_position = 0;

double timeElapsed;

bool verbose = false;
bool quitFlag = false;
bool moving = false;
bool stopMotion = false;

double home_pos = 50; // Default home position
double adjusted;
double offset;

struct timespec ts_now, ts_last;

bool newDataAvailable = false;
bool processingMotorCommand = false;
std::mutex queueMutex;
std::condition_variable dataCondition;

/// Data Structures for Depth and Positional Data
struct timewDepth {
    float time;
    float depth;
};

struct PositionData {
    double x, y, z; // Translational data
    double rx, ry, rz; // Rotational data
    double gantry; // Gantry angle
    bool beam_hold; // True or false
};

// Queues for Depth and Position Data
std::queue<timewDepth> depthQueue;
std::queue<PositionData> positionQueue;
timewDepth latestDepth;
PositionData latestPosition;

// General utility functions
void openLogFile(string filename) {
    logFile.open(filename, ios::out);
    if (!logFile.is_open()) {
        cerr << "Error opening log file!" << endl;
    }
}

void closeLogFile() {
    logFile.close();
}

double TimeDiff(timespec Tstart, timespec Tend) { // in us
    return 1e6*Tend.tv_sec + 1e-3*Tend.tv_nsec - (1e6*Tstart.tv_sec + 1e-3*Tstart.tv_nsec);
}

void myInterrupt(void) {
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &ts_now);
    if (TimeDiff(ts_last, ts_now) > falsepulseDelay) {
        ts_last = ts_now;
        if(Direction == 1) {
            sensorVal++;
        }
        if(Direction == -1) {
            sensorVal--;
        }
    }
}

void Stop() {
    moving = false;
    newMessage("Motion stopped");
}

void driveActuator(int Direction, int Speed) {
    int rightPWM = RPWM;
    int leftPWM = LPWM;

    switch(Direction) {
        case 1: // extension
            pwmWrite(rightPWM, Speed);
            pwmWrite(leftPWM, 0);
            break;
        case 0: // stopping
            pwmWrite(rightPWM, 0);
            pwmWrite(leftPWM, 0);
            break;
        case -1: // retraction
            pwmWrite(rightPWM, 0);
            pwmWrite(leftPWM, Speed);
            break;
    }
}

void driveToPoint3(long setPoint) // For continuous movement, short motor operation timeout duration
{
	moving = true;
	// Define the start time and the timeout period ( in microseconds)
	long long start_time = micros();
	long long timeout = 2000000; // 2 seconds timeout

	while (abs(sensorVal - setPoint) > 66 && moving) // the motor usually takes ~66 steps between telling it to stop and it actually stopping
	{
		if (setPoint < (sensorVal)) //addition gives buffer to prevent actuator from rapidly vibrating due to noisy data inputs
		{
			Direction = -1;
			driveActuator(Direction, Speed);
		}
		else if (setPoint > (sensorVal))
		{
			Direction = 1;
			driveActuator(Direction, Speed);
		}
		// check if the operation has exceeded the timeout period
		if(micros() - start_time > timeout)
		{
			cout << "Operation timeout. Stopping the motor" << endl;
			driveActuator(0, Speed);
			moving = false;
			return;
		}
		//usleep(500);
	}

	driveActuator(0, Speed);
	moving = false;
	cout << "Set point: " << setPoint << "\tActuator reading: " << sensorVal << endl;
}


high_resolution_clock::time_point Move(double depth, high_resolution_clock::time_point timestamp) //parameter in mm
{
    //timeinfo time;
    auto start_move_time = high_resolution_clock::now();
    
    stringstream mesSS;
    mesSS << setprecision(4) << fixed << "Received Data: " << depth << " mm";
    newMessage(mesSS.str());
    

    long moveTo = floor(depth*stepsPerMill);
    if (moveTo > 21800) // don't allow the motor to hit end of range
    {
	moveTo = 21800;
    }

    driveToPoint3(moveTo);
    
    auto end_Time = high_resolution_clock::now();
    auto move_duration = duration_cast<microseconds>(end_Time-start_move_time).count();
    float duration = move_duration/1000;
    std::cout << "Move duration: " << duration << "ms" << std::endl;
    return end_Time;
    
}

void moveTillLimit(int Direction, int Speed) //this function moves the actuator to one of its limits
{
    volatile long prevsensorVal=0;
    
    struct timespec ts_start, ts_current;
    do 
    {
		prevsensorVal = sensorVal;
		clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &ts_current);
		ts_start = ts_current;
		while(TimeDiff(ts_start, ts_current) < 50000)
		{ //keep moving until counter remains the same for a short duration of time
			driveActuator(Direction, Speed);
			clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &ts_current);
		}
    }
    while(prevsensorVal !=sensorVal); //loop until all counts remain the same
    sensorVal = 0;
}


// Depth Data Processing
void processMotorCommandDepth(timewDepth info, double offset) {
    double depth_mm = info.depth / 100;
    if (abs(depth_mm - offset) <= 40) {
        if (abs(depth_mm - offset) >= 0) {
            double error = depth_mm - offset;
            adjusted -= error;
            auto recv_time = high_resolution_clock::now();
            auto end_Time = high_resolution_clock::now(); // Simulating Move function
            logFile << info.time << " " << duration_cast<microseconds>(recv_time.time_since_epoch()).count() << " " << depth_mm << " " << adjusted << " Move" << endl;
        }
    }
}

// Position Data Processing
void processMotorCommandPosition(PositionData position, double offset) {
    double target = position.y;
    if (abs(target - offset) <= 40) {
        if (abs(target - offset) >= 0) {
            double error = target - offset;
            adjusted -= error;
            auto recv_time = high_resolution_clock::now();
            auto end_Time = high_resolution_clock::now(); // Simulating Move function
            logFile << duration_cast<microseconds>(recv_time.time_since_epoch()).count() << " " << target << " " << adjusted << " Move" << endl;
        }
    }
}

// Motor Control Thread Function
void motorControl(bool isDepth) {
    while (true) {
        std::unique_lock<std::mutex> lock(queueMutex);
        dataCondition.wait(lock, [] { return newDataAvailable; });

        if (isDepth) {
            if (!processingMotorCommand) {
                processingMotorCommand = true;
                timewDepth currentData = latestDepth;
                lock.unlock();
                processMotorCommandDepth(currentData, offset);
                lock.lock();
                processingMotorCommand = false;
                newDataAvailable = false;
            }
        } else {
            if (!processingMotorCommand) {
                processingMotorCommand = true;
                PositionData currentData = latestPosition;
                lock.unlock();
                processMotorCommandPosition(currentData, offset);
                lock.lock();
                processingMotorCommand = false;
                newDataAvailable = false;
            }
        }
    }
}

struct timewDepth {
	float time;
	float depth;
	
};
	
timewDepth reader1D(const char *data_from_client){
	timewDepth info;
	
		memcpy(&info.time, data_from_client+1, sizeof(float));
		memcpy(&info.depth, data_from_client+6, sizeof(float));

		return info;

} 

// UDP Receive Function for Depth
void receiveUDPDepthData(int socket, struct sockaddr_in* si_other, socklen_t* slen) {
    char buf[SIZE];
    while (true) {
        memset(buf, '\0', SIZE);
        if (recvfrom(socket, buf, SIZE, 0, (struct sockaddr *) si_other, slen) == -1) {
            cout << "Error receiving depth data" << endl;
            continue;
        }
        timewDepth info;
        memcpy(&info.time, buf + 1, sizeof(float));
        memcpy(&info.depth, buf + 6, sizeof(float));
        logFile << info.time << " " << info.depth / 100 << endl;
        std::lock_guard<std::mutex> lock(queueMutex);
        latestDepth = info;
        newDataAvailable = true;
        dataCondition.notify_one();
    }
}

struct PositionData {
	double x, y, z; // Translatetional data
	double rx, ry, rz; // Rotational data
	double gantry; // Gantry angle
	bool beam_hold; // True or false
};

PositionData readerKIM(const char *data_from_client){
		PositionData position;

		memcpy(&position.x, data_from_client, sizeof(double));
		memcpy(&position.y, data_from_client + sizeof(double), sizeof(double));
		memcpy(&position.z, data_from_client + 2* sizeof(double), sizeof(double));
		memcpy(&position.rx, data_from_client, 3*sizeof(double));
		memcpy(&position.ry, data_from_client + 4*sizeof(double), sizeof(double));
		memcpy(&position.rz, data_from_client + 5* sizeof(double), sizeof(double));
		memcpy(&position.gantry, data_from_client + 6*sizeof(double), sizeof(double));
		memcpy(&position.beam_hold, data_from_client + 7*sizeof(double), sizeof(bool));

		
		
		cout << "Received data: " << endl;
		cout << "X =  " << position.x << "mm" <<endl;
		cout << "Y =  " << position.y << "mm" << endl;
		cout << "Z =  " << position.z << "mm" << endl;
		cout << "rX =  " << position.rx << "mm" <<endl;
		cout << "rY =  " << position.ry << "mm" << endl;
		cout << "rZ =  " << position.rz << "mm" << endl;
		cout << "Gantry (in degree) =  " << position.gantry << endl;
		cout << "Beam hold: " << (position.beam_hold ? "true" : "False") << endl;
		
		return position;
		
	
}

// UDP Receive Function for Position
void receiveKIMUDPData(int socket, struct sockaddr_in* si_other, socklen_t* slen) {
    char buf[SIZE];
    while (true) {
        memset(buf, '\0', SIZE);
        if (recvfrom(socket, buf, SIZE, 0, (struct sockaddr *) si_other, slen) == -1) {
            cout << "Error receiving KIM data" << endl;
            continue;
        }
        PositionData position;
        memcpy(&position.x, buf, sizeof(double));
        memcpy(&position.y, buf + sizeof(double), sizeof(double));
        memcpy(&position.z, buf + 2 * sizeof(double), sizeof(double));
        logFile << duration_cast<microseconds>(high_resolution_clock::now().time_since_epoch()).count() << " " << position.y << endl;
        std::lock_guard<std::mutex> lock(queueMutex);
        latestPosition = position;
        newDataAvailable = true;
        dataCondition.notify_one();
    }
}

// Main function
int main() {
    wiringPiSetup();
    pinMode(RPWM, PWM_OUTPUT);
    pinMode(LPWM, PWM_OUTPUT);
    pinMode(_interrupt, INPUT);
    pullUpDnControl(_interrupt, PUD_DOWN);
    wiringPiISR(_interrupt, INT_EDGE_RISING, &myInterrupt);

    // Ask the user which mode to operate in
    cout << "Select data type for operation (1: Depth Data, 2: Positional Data): ";
    int choice;
    cin >> choice;

    bool isDepth = (choice == 1);
    if (isDepth) {
        openLogFile("DepthDataLog.txt");
        cout << "Operating in Depth Data Mode" << endl;
    } else {
        openLogFile("PositionDataLog.txt");
        cout << "Operating in Positional Data Mode" << endl;
    }

    int s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    sockaddr_in si_me, si_other;
    socklen_t slen = sizeof(si_other);

    memset((char *) &si_me, 0, sizeof(si_me));
    si_me.sin_family = AF_INET;
    si_me.sin_port = htons(PORT);
    si_me.sin_addr.s_addr = inet_addr("192.168.8.2");

    if (bind(s, (struct sockaddr *) &si_me, sizeof(si_me)) == -1) {
        cout << "Bind failed" << endl;
        return -1;
    }

    std::thread udpThread(isDepth ? receiveUDPDepthData : receiveKIMUDPData, s, &si_other, &slen);
    std::thread motorThread(motorControl, isDepth);

    udpThread.join();
    motorThread.join();

    close(s);
    closeLogFile();
    return 0;
}
