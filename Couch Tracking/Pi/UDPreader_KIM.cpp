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

volatile long lastDebounceTime_0=0; //timer for when interrupt was triggered
volatile int stepsPerMill = 155;

int Speed = 1023; //choose any speed in the range [0, 1023]

double falsepulseDelay = 10; //10us delay

volatile long sensorVal=0; 

int Direction; //-1 = retracting
               // 0 = stopped
               // 1 = extending

long pulseTotal=0; //stores number of pulses in one full extension/actuation

double mean_depth = 0, current_position = 0;

const double centreOfROM = 75; //mm

struct timespec ts_now, ts_last;
double  timeElapsed;

bool verbose = false;
bool quitFlag = false;
bool moving = false;
bool stopMotion = false;



void openLogFile() {
    logFile.open("couch_only_25s_10mm_1.txt", ios::out);
    if (!logFile.is_open()) {
	cerr << "Error opening log file!" << endl;
    }
}

void closeLogFile() {
    logFile.close();
}


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
	usleep(500);
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


struct PositionData {
	double x, y, z, gantry;
	bool beam_hold;
};

PositionData readerKIM(const char *data_from_client){
		PositionData position;

		memcpy(&position.x, data_from_client, sizeof(double));
		memcpy(&position.y, data_from_client + sizeof(double), sizeof(double));
		memcpy(&position.z, data_from_client + 2* sizeof(double), sizeof(double));
		memcpy(&position.gantry, data_from_client + 3*sizeof(double), sizeof(double));
		memcpy(&position.beam_hold, data_from_client + 4*sizeof(double), sizeof(bool));
		
		// Convert cm to mm
		position.x *= 10.0;
		position.y *= 10.0;
		position.z *= 10.0;
		
		
		cout << "Received data: " << endl;
		cout << "X =  " << position.x << endl;
		cout << "Y =  " << position.y << endl;
		cout << "Z =  " << position.z << endl;
		cout << "Gantry (in degree) =  " << position.gantry << endl;
		cout << "Beam hold: " << (position.beam_hold ? "true" : "False") << endl;
		
		return position;
		
	
}

double home_pos = 50; // 80mm
double adjusted;
double offset;


std::queue<PositionData> dataQueue; // First in, first out data strucutre. Element is added to the back of the queue
std::mutex queueMutex;
std::condition_variable dataCondition;
bool newDataAvailable = false;
bool processingMotorCommand = false;
PositionData latestPosition; 



/// UDP reader ////
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



void receiveKIMUDPData(int socket, struct sockaddr_in* si_other, socklen_t* slen) {
    char buf[SIZE];
    while (true) {
		memset(buf, '\0', SIZE);
		
		if (recvfrom(socket, buf, SIZE, 0, (struct sockaddr *) si_other, slen) == -1) {
			cout << "Error in receving data" << endl;
			continue;

		}
		PositionData position = readerKIM(buf);
		auto receive_time = high_resolution_clock::now();
	        logFile << duration_cast<microseconds>(receive_time.time_since_epoch()).count() << " " << position.x <<std::endl;
		

	    {
		
	    std::cout << "Timestamp: " << duration_cast<microseconds>(receive_time.time_since_epoch()).count() << ", Position: " << position.x << "mm" << std::endl;
	    std::lock_guard<std::mutex> lock(queueMutex);
	    latestPosition = position;
	    newDataAvailable = true;
	}
            dataCondition.notify_one();
        
    }
}	


//////// Motion compensation ////////////



// Motion compensation algorithm
void processMotorCommand(PositionData position, double offset) {
    double target = position.x;

    
    if (abs(target - offset) <= 40) {
        if (abs(target - offset) >= 1 ) {
            double error = target - offset;
	    
	    std::cout << "error is: " << error << std::endl;

            adjusted = adjusted - error;
            
            std::cout << "Target at: " << target << ", adjusted couch position: " << adjusted << std::endl;
            // Get the current timestamp
	    auto recv_time = high_resolution_clock::now();
	    auto end_Time = Move(adjusted, recv_time);
	    
	    
	    logFile << duration_cast<microseconds>(recv_time.time_since_epoch()).count() << " " << target << " " << adjusted << " " << "Move" <<endl;
        } else {
	    auto out_time = high_resolution_clock::now();
        
        logFile << duration_cast<microseconds>(out_time.time_since_epoch()).count() << " " << target << " " << "N/A" << " " << "Noise" <<std::endl;
    }
    } else {
	auto start_time = high_resolution_clock::now();
        std::cout << "Reading exceeds limit." << (abs(target - offset)) <<std::endl;
        logFile << duration_cast<microseconds>(start_time.time_since_epoch()).count() << " " << target << " " << "N/A" << " " << "Large" <<std::endl;
    }
}

// Motor control thread function
void motorControl() {
    while (true) {
        std::unique_lock<std::mutex> lock(queueMutex);
        dataCondition.wait(lock, []{ return newDataAvailable; }); // Wait for new data
	
        if (!processingMotorCommand) {
	    
	    processingMotorCommand = true; // Start processing 
	    PositionData currentData = latestPosition; // Get the latest data point
	    lock.unlock();
            processMotorCommand(currentData, offset); // Process the motor command

            lock.lock(); // lock again before updating status
            processingMotorCommand = false;
            newDataAvailable = false; // Notify that processing is finished
        } else {
	    auto in_time = high_resolution_clock::now();
	    logFile << duration_cast<microseconds>(in_time.time_since_epoch()).count() << " " <<latestPosition.x << " " << "N/A"  << " " << "SKIP" <<std::endl;
            lock.unlock();
        }
    }
}


/////////////////////////////////////////////

	
int main() {
	// setting up the pi
    wiringPiSetup();
	
    pinMode(RPWM,PWM_OUTPUT);
    pinMode(LPWM,PWM_OUTPUT);
    pwmWrite(RPWM, 0);
    pwmWrite(LPWM, 0);

    pinMode(_interrupt, INPUT);
    pullUpDnControl(_interrupt, PUD_DOWN);

    wiringPiISR(_interrupt, INT_EDGE_RISING, &myInterrupt);
	
    pulseTotal = 0;
    cout << "Drive motor to home" << endl;
    Direction = -1;
    moveTillLimit(Direction, Speed);
    usleep(500);
    
    PrintThisIPAddress();
	
    int s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    sockaddr_in si_me, si_other;
    socklen_t slen = sizeof(si_other);
  
	if ((s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
		cout << "Failed to create receive socket" << endl;
		return -1;
	}
	
	memset((char *) &si_me, 0, sizeof(si_me));
	si_me.sin_family = AF_INET;
	si_me.sin_port = htons(PORT);
	si_me.sin_addr.s_addr = inet_addr("192.168.8.2"); // Router IP address
	
	if (bind(s,(struct sockaddr *) &si_me, sizeof(si_me)) == -1) {
		cout << "Bind failed" << endl;
		return -1;
	}
	
	cout << "Socket created, UDP listening ... " << endl;
	

	
	cout<< "Move motor to set home position " << home_pos<< "mm" <<endl;
	Move2(home_pos);
	usleep(500);
	//////////////////////
	cout << "Enter the tracking object desired position: ";
	cin >> offset; // Offset, the initial home/zero position of the tracking target, also where we would like the object to stay 
	
	// Wait for user input to start listening for UDP transmissions
	cout << "Press enter to start listening for UDP transmissions..." << endl;
	cin.get();
	//////////////////////
	
		
	// Open the log file
	openLogFile();
  
    std::thread udpThread(receiveKIMUDPData, s, &si_other, &slen);
  //double latestDepth = 0.0;
  
    std::thread motorThread(motorControl);

    motorThread.join();
    udpThread.join();
	
	close(s);
	closeLogFile();

	return (0);
	
    }
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	/*
	double home_pos = 80; // 80mm
	
	cout<< "Move motor to set home position " << home_pos<< "mm" <<endl;
	Move2(home_pos);
	usleep(500);
	double adjusted = home_pos;
	
	// Ask the user for an offset value
	double offset;
	cout << "Enter the tracking object desired position: ";
	cin >> offset; // Offset, the initial home/zero position of the tracking target, also where we would like the object to stay 
	
	// Open the log file
	openLogFile();
	//double adjusted;
	

	
	while (true) {
		memset(buf, '\0', SIZE);
		if (recvfrom(s, buf, SIZE, 0, (struct sockaddr *) &si_other, (socklen_t *) &slen) == -1) {
			cout << "Error in receving data" << endl;
			break;

		}
		if (buf[0] == 'c' && buf[5] == 't') {
		    timewDepth info = reader1D(buf); // Parse UDP data and extract positional information
		    double depth_mm = info.depth/100;
		    std::cout << "At frame No: " << info.time << ", depth is: " << depth_mm <<std::endl;
		    double error = 0 - depth_mm;
		    double adjusted = adjusted + error;
		    //double adjusted = offset -(depth_mm - home_pos);
		    auto recv_time = high_resolution_clock::now();
		    auto move_timestamp = Move(adjusted, recv_time);
		    logFile << info.time << " " << duration_cast<microseconds>(move_timestamp.time_since_epoch()).count() << " " << depth_mm << " " << adjusted << endl;
		}
		
	    }
	    
		///////
		// Check if the received data starts with 't'
		if (buf[0] == 't') {
			// convert the received data to depth (mm)
			uint64_t num = 0;
			for (int32_t i = 9; i>0; i--) {
				num = (num<<8) + (buf[i] & 0xFF);
			}
			double depth = num / 100.0; // Convert to mm
			
			std::cout << "Received Depth: " << depth << " mm" << std::endl;

	}
	
    

///////
	
		
	close(s);
	closeLogFile();
	return (0);
    }

		
*/
