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
	        //logFile << duration_cast<microseconds>(receive_time.time_since_epoch()).count() << " " << position.x <<std::endl;
	        //cout <<"x"<< position.x <<  endl;
		

	    {
		
	    std::cout << "Timestamp: " << duration_cast<microseconds>(receive_time.time_since_epoch()).count() << ", Position: " << position.x << "mm" << std::endl;
	    //std::lock_guard<std::mutex> lock(queueMutex);
	    //latestPosition = position;
	    //newDataAvailable = true;
	}
            //dataCondition.notify_one();
        
    }
}	

int main() {
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
	
	std::thread udpThread(receiveKIMUDPData, s, &si_other, &slen);
	udpThread.join();
	
	close(s);
	
	return (0);
	
	
	

	}
