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
#include <utility> // For std::pair
#include "logger.cpp"

#define SIZE 512
#define PORT 1400
#define MOTOR_UDP_PORT 2400
const char* ipAddress = "0.0.0.0"; // Set to Raspberry Pi

// Router 192.168.8.2
// Sender 192.168.8.190
using namespace std;
using namespace std::chrono;

ofstream logFile; // Global file stream for logging

//int RPWM=26; //PWM signal right side
//int LPWM=23; 
//int _interrupt = 15;

//volatile long lastDebounceTime_0=0; //timer for when interrupt was triggered
//volatile int stepsPerMill = 155;

// Motor parameters
double home_pos = 50; // 80mm
double adjusted;
double offset;

//int Speed = 1023; //choose any speed in the range [0, 1023]
const double MOTOR_VELOCITY = 12.0; // Simulate motor velocity here, mm/s

//double falsepulseDelay = 10; //10us delay

//volatile long sensorVal=0; 
//double prevDepth = 0; 

//int Direction; //-1 = retracting
               // 0 = stopped
               // 1 = extending

//long pulseTotal=0; //stores number of pulses in one full extension/actuation

//double mean_depth = 0, current_position = 0;

//const double centreOfROM = 75; //mm

//struct timespec ts_now, ts_last;
//double  timeElapsed;

/// processMotorCommand thread parameter ///
bool verbose = false;
bool quitFlag = false;
bool moving = false;
bool stopMotion = false;

std::mutex queueMutex;
std::condition_variable dataCondition;
bool newDataAvailable = false;
bool processingMotorCommand = false;


/// Running log ////

void openLogFile() {
    logFile.open("EMULATOR Log.txt", ios::out);
    if (!logFile.is_open()) {
	cerr << "Error opening log file!" << endl;
    }
}

void closeLogFile() {
    logFile.close();
}
/*
////////////////////////

/// Motor Mechanism /////

double TimeDiff(timespec Tstart, timespec Tend) //in us
{
    return 1e6*Tend.tv_sec + 1e-3*Tend.tv_nsec - (1e6*Tstart.tv_sec + 1e-3*Tstart.tv_nsec);
}

void myInterrupt(void)
{	
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &ts_now);
	
    //This interrupt function increments a counter corresponding to changes in the optical pin status
    if (TimeDiff(ts_last,ts_now) > falsepulseDelay) //reduce noise by debouncing IR signal 
    { 
	ts_last = ts_now;  
	if(Direction==1)
	{
	    sensorVal++;
	    //cout << "\tsensorVal ++....\t" << sensorVal << endl;
	}
	if(Direction==-1)
	{
	    sensorVal--;
	    //cout << "\tsensorVal --....\t" << sensorVal << endl;
	}
    }
}

void Stop() 
{
    moving = false;
    newMessage("Motion stopped");
}

void driveActuator(int Direction, int Speed)
{
    int rightPWM=RPWM;
    int leftPWM=LPWM;

    switch(Direction)
    {
	case 1: //extension
	    pwmWrite(rightPWM, Speed);
	    pwmWrite(leftPWM, 0);
	  break;

	case 0: //stopping
	    pwmWrite(rightPWM, 0);
	    pwmWrite(leftPWM, 0);
	break;

	case -1: //retraction
	    pwmWrite(rightPWM, 0);
	    pwmWrite(leftPWM, Speed);
	break;
    }
}

void driveToPoint(long setPoint)
{
    moving = true;
    while (abs(sensorVal - setPoint) > 66 && moving) // the motor usually takes ~66 steps between telling it to stop and it actually stopping
    {
	if(setPoint < (sensorVal)) //addition gives buffer to prevent actuator from rapidly vibrating due to noisy data inputs
	{               
	    Direction = -1;
	    driveActuator(Direction, Speed);
	}
	else if(setPoint > (sensorVal))
	{             
	    Direction = 1;
	    driveActuator(Direction, Speed);
	}
	//usleep(500);
    }
    driveActuator(0, Speed);
    moving = false;
    cout << "Set point: " << setPoint << "\tActuator reading: " << sensorVal << endl;
}

void driveToPoint2(long setPoint)
{
	moving = true;
	// Define the start time and the timeout period ( in microseconds)
	long long start_time = micros();
	long long timeout = 8000000; // 8 seconds timeout

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
		usleep(500);
	}

	driveActuator(0, Speed);
	moving = false;
	cout << "Set point: " << setPoint << "\tActuator reading: " << sensorVal << endl;
}
void driveToPoint3(long setPoint) // For continuous movement, short motor operation timeout duration
{
	moving = true;
	// Define the start time and the timeout period ( in microseconds)
	long long start_time = micros();
	long long timeout = 1000000; // 1 seconds timeout

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
		usleep(500);
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


void Move2(double depth) //parameter in mm
{
    stringstream mesSS;
    mesSS << setprecision(4) << fixed << "Received Data: " << depth << " mm";
    newMessage(mesSS.str());
    

    long moveTo = floor(depth*stepsPerMill);
    if (moveTo > 21800) // don't allow the motor to hit end of range
    {
	moveTo = 21800;
    }

    driveToPoint2(moveTo);
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
/////////////////////////
*/
// Change this code into simulating the motor motion and execute duration 
// Return motor move timestamp and duration 

double Move(double depth, double error) //parameter in mm
{
    //timeinfo time;
    auto start_move_time = high_resolution_clock::now();
    
    stringstream mesSS;
    mesSS << setprecision(4) << fixed << "Motor position: " << depth << " mm";
    newMessage(mesSS.str());
    
    // Calculate the moving duration based on velocity
    double move_duration_ms = std::abs((error / MOTOR_VELOCITY)*1000.0);
    usleep(static_cast<useconds_t>(move_duration_ms*1000));
    
    auto end_Time = high_resolution_clock::now();
    auto move_duration = duration_cast<milliseconds>(end_Time-start_move_time).count();
    float duration = move_duration_ms;
    std::cout << "Move duration: " << duration << "ms" << std::endl;
    return static_cast<double> (move_duration);
    
}

/// UDP data format ///
/// Data Structures for Depth measurement



// Depth measurement
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
/*
// Data structure for KIM data
struct PositionData {
    double x, y, z; // Translational data
    double rx, ry, rz; // Rotational data
    double gantry; // Gantry angle
    bool beam_hold; // True or false
};

// Decode incoming KIM data point
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
		//cout << "X =  " << position.x << "mm" <<endl;
		cout << "Y =  " << position.y << "mm" << endl;
		//cout << "Z =  " << position.z << "mm" << endl;
		//cout << "rX =  " << position.rx << "mm" <<endl;
		//cout << "rY =  " << position.ry << "mm" << endl;
		//cout << "rZ =  " << position.rz << "mm" << endl;
		//cout << "Gantry (in degree) =  " << position.gantry << endl;
		//cout << "Beam hold: " << (position.beam_hold ? "true" : "False") << endl;
		
		return position;
		
	
}
*/

struct PositionData {
    double y;
   
}; 

PositionData readerKIM(const char *data_from_client) {
    PositionData position;

    memcpy(&position.y, data_from_client, sizeof(double));
    
    // Print received data
    std::cout << "Received data: " << std::endl;
    std::cout << "Y = " << position.y << " mm" << std::endl;  // Keeping only Y for now

    return position;
}

// Queues for Depth and Position Data
std::queue<timewDepth> depthQueue;
std::queue<PositionData> positionQueue;
timewDepth latestDepth;
PositionData latestPosition;

// UDP Receive Function for Depth

void receiveUDPDepthData(int socket, struct sockaddr_in* si_other, socklen_t* slen) {
    char buf[SIZE];
    while (true) {
        memset(buf, '\0', SIZE);
        if (recvfrom(socket, buf, SIZE, 0, (struct sockaddr *) si_other, slen) == -1) {
            cout << "Error receiving depth data" << endl;
            continue;
        }
        timewDepth info = reader1D(buf);
        auto receive_time = high_resolution_clock::now();
	    logFile << info.time<<" " << duration_cast<microseconds>(receive_time.time_since_epoch()).count() << " " << info.depth/100 <<std::endl;
       
        std::lock_guard<std::mutex> lock(queueMutex);
        latestDepth = info;
        newDataAvailable = true;
        dataCondition.notify_one();
    }
}



void receiveKIMUDPData(int socket, struct sockaddr_in* si_other, socklen_t* slen) {
    char buf[SIZE];
    while (true) {
        memset(buf, '\0', SIZE);
	*slen = sizeof(sockaddr_in); // Reset before every recvform
        if (recvfrom(socket, buf, SIZE, 0, (struct sockaddr*)si_other, slen) == -1) {
            cout << "Error receiving KIM data" << endl;
            continue;
        }
	
	// Debug log sender IP
	char sender_ip[INET_ADDRSTRLEN];
	inet_ntop(AF_INET, &si_other->sin_addr, sender_ip, INET_ADDRSTRLEN);
	std::cout << "[Couch] Received data from: " << sender_ip << ":" << ntohs(si_other->sin_port) << std::endl;
        PositionData position = readerKIM(buf);

        logFile << duration_cast<microseconds>(high_resolution_clock::now().time_since_epoch()).count() << " " << position.y << endl;
        std::lock_guard<std::mutex> lock(queueMutex);
        latestPosition = position;
        newDataAvailable = true;
        dataCondition.notify_one();
    }
}

////////////////////////



/// UDP communication ////
void PrintThisIPAddress()
{
    struct ifaddrs *ifap, *ifa;
    struct sockaddr_in *sa;
    char *addr;
    getifaddrs(&ifap);
    for (ifa = ifap; ifa; ifa = ifa->ifa_next)
    {
	if (ifa->ifa_addr && ifa->ifa_addr->sa_family==AF_INET)
	{
	    sa = (struct sockaddr_in *) ifa->ifa_addr; 
	    addr = inet_ntoa(sa->sin_addr);
	    if (strcmp(ifa->ifa_name,"wlan0") == 0)
		cout << "IP Address for UDP: " << addr << " (wlan0)" << endl;
	    else if (strcmp(ifa->ifa_name,"eth0") == 0)
		cout << "IP Address for UDP: " << addr << " (eth0)" << endl;
	}
    }
}


void UDPSendMotorMotion(double error, const sockaddr_in& client_addr) {
    double compensation = -error;
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("[Couch] Send socket creation failed");
        return;
    }

    sockaddr_in send_addr;
    memset(&send_addr, 0, sizeof(send_addr));
    send_addr.sin_family = AF_INET;
    send_addr.sin_addr = client_addr.sin_addr;
    send_addr.sin_port = client_addr.sin_port;  // <- FIX: use sender’s actual source port

    char ipStr[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &(send_addr.sin_addr), ipStr, INET_ADDRSTRLEN);
    std::cout << "[Couch] Sending feedback to: " << ipStr << ":" << ntohs(send_addr.sin_port) << std::endl;

    ssize_t sent = sendto(sock, &compensation, sizeof(double), 0, (struct sockaddr*)&send_addr, sizeof(send_addr));
    if (sent < 0) {
        perror("[Couch] Failed to send feedback");
    } else {
        std::cout << "[Couch] Sent motor compensation feedback: " << error << std::endl;
        logFile << duration_cast<milliseconds>(high_resolution_clock::now().time_since_epoch()).count()
                << ", Sent feedback: " << error << endl;
    }
    close(sock);
}

    
    
/////////////////////////////////////////////////






//////// Motion compensation //////////// 

// Come up with something that only do replication ///////////////////

// Depth Data Processing
// Determine couch position according to received depth measurement
void processMotorCommandDepth(timewDepth info, double offset) {
    double depth_mm = info.depth / 100;

    if (abs(depth_mm - offset) <= 40) {
        if (abs(depth_mm - offset) >= 0) {
            double error = -(depth_mm - offset);
            //adjusted -= error;
	    double distance = adjusted+error;
            auto recv_time = high_resolution_clock::now();
            double duration = Move(distance,error);
	    auto end_time = high_resolution_clock::now();
            logFile << info.time << " " << duration_cast<microseconds>(end_time.time_since_epoch()).count() << " " << depth_mm << " " << adjusted << " Move" << endl;
        }
    }
}


// Position Data Processing
// Determine couch position according to received depth measurement
// KIM delay added
void processMotorCommandPosition(PositionData position, double offset, const sockaddr_in& client_addr) {
    double KIM_latency = 0; // in ms 
    double target = position.y;
    if (abs(target - offset) <= 40) { // Offset = 0
        if (abs(target - offset) >= 0) {
            double error = target - offset;
            adjusted -= error;
            auto recv_time = high_resolution_clock::now();
            double duration = (Move(adjusted, error));
	    auto end_time = high_resolution_clock::now();
	    
	                    
	    // Slow down the couch response
	    if (duration < KIM_latency){
			
		    double delay = (KIM_latency - duration);
		    std::cout << "Delay: " << delay << "ms" << std::endl;
		    usleep(static_cast<useconds_t>(delay*1000));
		}
	    UDPSendMotorMotion(error, client_addr); // Send the motor displacement via UDP 
            logFile << duration_cast<microseconds>(end_time.time_since_epoch()).count() << " " << target << " " << adjusted << " Move" << endl;
        }
    }
}
// Modify this code so that it output the motor position after moving is done
// Add UDP sender function, send this positional information to Measurement system

// Motor Control Thread Function
// If motor is on, ignore all data coming in
// if motor is off, it becomes available for another movement and take the next coming in data point
void motorControl(bool isDepth, const sockaddr_in& client_addr) {
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
        } else { // Only KIM data format code was changed to adapt emulator function
            if (!processingMotorCommand) {
                processingMotorCommand = true;
                PositionData currentData = latestPosition;
                lock.unlock();
                processMotorCommandPosition(currentData, offset, client_addr);
                lock.lock();
                processingMotorCommand = false;
                newDataAvailable = false;
            }
        }
    }
}

/////////////////////////////////////////////


	
	
// Main function
int main() {
    //wiringPiSetup();
    //pinMode(RPWM, PWM_OUTPUT);
    //pinMode(LPWM, PWM_OUTPUT);
    //pwmWrite(RPWM, 0);
    //pwmWrite(LPWM, 0);
    //pinMode(_interrupt, INPUT);
    //pullUpDnControl(_interrupt, PUD_DOWN);
    //wiringPiISR(_interrupt, INT_EDGE_RISING, &myInterrupt);

    //pulseTotal = 0;

    cout << "Drive motor to home" << endl;
    //Direction = -1;
    //moveTillLimit(Direction, Speed);
    //Move(0);
    usleep(500);
    PrintThisIPAddress();
    
    cout<< "Move motor to set home position " << home_pos<< "mm" <<endl;
	//Move2(home_pos);
	usleep(500);

    sockaddr_in si_me{};
    sockaddr_in si_other{};
    socklen_t slen = sizeof(si_other);
    char buf[SIZE];
    
    int s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if ((s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
		cout << "Failed to create receive socket" << endl;
		return -1;
	}

    //memset((char *) &si_me, 0, sizeof(si_me));
    si_me.sin_family = AF_INET;
    si_me.sin_port = htons(PORT);
    si_me.sin_addr.s_addr = inet_addr(ipAddress); // Give IP address here "192.168.8.2"
	
    if (si_me.sin_addr.s_addr == INADDR_NONE) {
        std::cerr << "Invalid IP address format: " << ipAddress << std::endl;
        return 1;
    }

    if (bind(s, (struct sockaddr *) &si_me, sizeof(si_me)) == -1) {
        cout << "Bind failed" << endl;
        return -1;
    }
	cout << "Socket created, UDP listening ... " << endl;
	
    // Ask the user which mode to operate in
    cout << "Select data type for operation: [1], Depth Data (Do not choose this in emulator mode), [2], Positional Data ";
    int choice;
    cin >> choice;

    bool isDepth = (choice == 1);
    if (isDepth) {
        cout << "Operating in Depth Data Mode" << endl;
        std::cout << "Gathering 30 frames to calculate offset..." << std::endl;
    
        // Variables to calculate average
        std::vector<double> depths;
        depths.reserve(30);
        // Wait for 30 frames of data
        while (depths.size() < 30) {
                char buf[SIZE];
                memset(buf, '\0', SIZE);
                
                if (recvfrom(s, buf, SIZE, 0, (struct sockaddr *) &si_other, (socklen_t *) &slen) == -1) {
                    std::cout << "Error in receiving data" << std::endl;
                    continue;
                }
                
                if (buf[0] == 'c' && buf[5] == 't') {
                    timewDepth info = reader1D(buf);
                    double depth_mm = info.depth / 100;
                    depths.push_back(depth_mm);
                    std::cout << "Received frame " << depths.size() << ": Depth = " << depth_mm << " mm" << std::endl;
            }
        }
        // Calculate average depth
        double sum = std::accumulate(depths.begin(), depths.end(), 0.0);
        double average_depth = sum / depths.size();
        
            
        // Use average depth as the offset
        offset = average_depth;
        std::cout << "Calculated offset: " << offset << " mm" << std::endl;
        adjusted = home_pos;
        openLogFile();
        
    } else {
        openLogFile();
        cout << "Operating in Positional Data Mode" << endl;
        adjusted = home_pos;
        offset = 0;
    }

    std::thread udpThread(isDepth ? receiveUDPDepthData : receiveKIMUDPData, s, &si_other, &slen);
    std::thread motorThread(motorControl, isDepth, std::ref(si_other));

    udpThread.join();
    motorThread.join();

    close(s);
    closeLogFile();
    return 0;
}
