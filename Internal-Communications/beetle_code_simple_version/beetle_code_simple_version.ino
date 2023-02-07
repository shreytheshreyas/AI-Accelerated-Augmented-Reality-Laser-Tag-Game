#define DATA_RATE 115200 //Defining datarate to be 115200 baud
#define PACKET_SIZE 20 //Defining packet size to be 20 bytes

#define BEETLE_ID 0 //Need to change this for each and every beetle
#define SEQUENCE_NUMBER 1
#define PACKET_TYPE 2

#define ACK 65 //The letter 'A' corresponds to the ASCII code 65
	       //
byte dataPacket[PACKET_SIZE];
int sequenceNumber = 0;
bool condition = false;
void create_data_packet(float data) {
	//TODO: Need to define code over here
}

void create_handshake_packet() {
 
}

void send_ack_packet() {

  Serial.write("A");
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
//  Serial.write(0);
}
void handshake_mechanism(bool isHandShakeComplete) {
	int receivedData = Serial.read();
	bool completionStatus = false;

	//If received packet is 'S', create ACK packet and send to the relay node
	if(receivedData == 83) 
		Serial.write(ACK);
	
	//If received packet is 'A' set complettionStatus to True
	if(receivedData == 65)
		completionStatus = true;
	
	
	return completionStatus;
}

void setup(void) {
  Serial.begin(115200);
}

void loop(void) {
//	bool isHandshakeComplete = false;
//	if (!isHandshakeComplete)
//		isHandshakeComplete = handshake_mechanism()
//	
//	if (isHandshakeComplete) 
//		//TODO: Data-Transfer can occur
//  dataPacket[0] = (byte) 65;
//  for (int i = 1; i < PACKET_SIZE; i++) {
//    dataPacket[i] = (byte) 65;
//  }

//  Serial.write(dataPacket,sizeof(dataPacket));

//  if(!condition)
    send_ack_packet();
    delay(1000);
//  condition = !condition;
  condition = true;
}
