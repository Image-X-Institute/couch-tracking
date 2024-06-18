#include <wiringPi.h>
#include <stdio.h> //printf
#include <string>
#include <stdlib.h>
#include <iostream>
#include <sstream>
#include <pthread.h>

#include <chrono>
#include <ctime>
#include <fstream>

using namespace std;
using namespace std::chrono;

stringstream logNameSS;

time_t rawtime;
struct tm * timeinfo;
char buffer[80];

void newMessage(string msg)
{
	cout << msg << endl;
	
	time(&rawtime);
	timeinfo = localtime(&rawtime);
	strftime(buffer,sizeof(buffer),"%d-%m-%Y_%H:%M:%S", timeinfo);
	ofstream logOut;
	logOut.open(logNameSS.str(),std::ofstream::app);

	logOut << "[ " << buffer << " ]\t" << msg << endl;
	logOut.close();
}

int LoggerMain(string logName)
{	
	//const struct sched_param priority = {99};
	//pthread_setschedparam(pthread_self(), SCHED_FIFO, &priority);
	
	//getting current time for log file identifier
	//	time_t rawtime;
	//	struct tm * timeinfo;
	//	char buffer[80];
	time(&rawtime);
	timeinfo = localtime(&rawtime);
	strftime(buffer,sizeof(buffer),"%d-%m-%Y_%H:%M:%S", timeinfo);
	
	//stringstream logNameSS;
	string logNameStart = "couchLogs/";
	logNameSS << logNameStart << logName << "_" << buffer << ".txt";
	ofstream logOut;
	logOut.open(logNameSS.str());
	logOut.close();
	
	cout << "Writing to file: " << logNameSS.str() << endl;

	return 0;
}
