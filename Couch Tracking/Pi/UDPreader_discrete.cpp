#include <wiringPi.h>
#include <wiringSerial.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <thread>
#include <cmath>

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

#include "logger.cpp"

#define SIZE 512
#define PORT 1400

using namespace std;
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

void Move(double depth) //parameter in mm
{
    stringstream mesSS;
    mesSS << setprecision(4) << fixed << "Received Data: " << depth << " mm";
    newMessage(mesSS.str());

    long moveTo = floor(depth*stepsPerMill);
    if (moveTo > 21800) // don't allow the motor to hit end of range
    {
	moveTo = 21800;
    }

    driveToPoint(moveTo);
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
	
void reader1D(const char *data_from_client){
	double time,depth;
	
		memcpy(&time, data_from_client, sizeof(double));
		memcpy(&depth, data_from_client + sizeof(double), sizeof(double));

		cout << "Received data: " << endl;
		cout << "Time " << time << endl;
		cout << "depth =  " << depth << endl;

} 
	
	
	
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
    //sensorVal=0;
    
	PrintThisIPAddress();
	
	struct sockaddr_in si_me, si_other;

	int s, slen = sizeof(sockaddr_in);
	char buf[SIZE];
	
	if ((s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
		cout << "Failed to create receive socket" << endl;
		return -1;
	}
	
	memset((char *) &si_me, 0, sizeof(si_me));
	si_me.sin_family = AF_INET;
	si_me.sin_port = htons(PORT);
	si_me.sin_addr.s_addr = inet_addr("172.20.10.2");
	
	if (bind(s,(struct sockaddr *) &si_me, sizeof(si_me)) == -1) {
		cout << "Bind failed" << endl;
		return -1;
	}
	
	cout << "Socket created, UDP listening ... " << endl;
	
	double home_pos = 100; // 100mm
	
	cout<< "Move motor to set home position" << home_pos<< "mm" <<endl;
	Move(home_pos);
	
	
	while (true) {
		memset(buf, '\0', SIZE);
		if (recvfrom(s, buf, SIZE, 0, (struct sockaddr *) &si_other, (socklen_t *) &slen) == -1) {
			cout << "Error in receving data" << endl;
			break;

		}
		//PositionData positionData = readerKIM(buf); // Parse UDP data and extract positional information
		// SET THE HOME POSITION FOR MOTOR
		
		//double adjusted = positionData.x + home_pos;
		
		//Move(adjusted);
		
		
		// Check if the received data starts with 't'
		if (buf[0] == 't') {
			// convert the received data to depth (mm)
			uint64_t num = 0;
			for (int32_t i = 9; i>0; i--) {
				num = (num<<8) + (buf[i] & 0xFF);
			}
			double depth = num / 100.0; // Convert to mm
			
			std::cout << "Received Depth: " << depth << " mm" << std::endl;
			double adjusted = depth + home_pos;
		
		    	Move(adjusted);
		

	}
	
	


	}
		
	close(s);

	return (0);
}
		
	
	
