#include "CRC.h"
#include "CRC8.h"

#define DATA_RATE 115200 //Defining datarate to be 115200 baud
#define PACKET_SIZE 20 //Defining packet size to be 20 bytes

#define BEETLE_ID 0 //Need to change this for each and every beetle
#define SEQUENCE_NUMBER 1
#define PACKET_TYPE 2

#define ACK 65 //The letter 'A' corresponds to the ASCII code 65
	       //
uint_8 dataPacket[PACKET_SIZE];
uint_8 sequenceNumber = 0;

void create_data_packet(float data) {
	//TODO: Need to define code over here
}

void create_handshake_packet() {

}

void handshake_mechanism(bool isHandShakeComplete) {
	int receivedPacket = Serial.read();
	bool completionStatus = false;

	//If received packet is 'S', create ACK packet and send to the relay node
	if(relayNodeData == 83) 
		Serial.write(ACK);
	
	//If received packet is 'A' set complettionStatus to True
	if(receivedData == 65)
		completionStatus = true;
	
	
	return completionStatus	
}

void setup(void) {

}

void loop(void) {
	bool isHandshakeComplete = false;
	if (!isHandshakeComplete)
		isHandshakeComplete = handshake_mechanism()
	
	if (isHandshakeComplete) 
		//TODO: Data-Transfer can occur
}
