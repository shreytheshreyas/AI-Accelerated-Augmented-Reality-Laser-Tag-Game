#define DATA_RATE 115200 //Defining datarate to be 115200 baud
#define PACKET_SIZE 20 //Defining packet size to be 20 bytes

#define BEETLE_DEVICE 0 //Need to change this for each and every beetle

//Packet Indices 
#define BEETLE_ID 0
#define SEQUENCE_NUMBER 1
#define PACKET_TYPE 2

#define ACK 'A' //The letter 'A' corresponds to the ASCII code 65
#define SYN 'S'

class Packet {
  private:
    float imu_gx;
    float imu_gy;
    float imu_gz;
    float imu_ax;
    float imu_ay;
    float imu_az;
    
    uint8_t packet_message[20];
  public:
    void getImuData();
    void getGunData();
    void getVestData();
    
    Packet() {
      getImuData();
      getGunData();
      getVestData();
      
      packet_message[BEETLE_ID] = BEETLE_DEVICE;
      packet_message[SEQUENCE_NUMBER] = BEETLE_DEVICE;
      for(int i = 0; i < PACKET_SIZE; i++) 
        packet_message[i] = 0;
    }
    
    Packet(uint8_t packetType) {
      packet_message[BEET
};


class ImuDataPacket: public Packet {
  private: 
    float gx;
    float gy;
    float gz;
    float ax;
    float ay;
    float az;
    
  public:
    void getImuData();
    ImuDataPacket() {
      this.getImuData();
      this.Packet('I')
    }
};

class GunDataPacket: public Packet {
  private:
    int address;
    int command;

  public:
    void getGunData();
    GunDataPacket() {
      this.getGunData();
      this.  
    }
};

class VestDataPacket: public Packet {
  private:
    int address;
    int command;

    public:
      void 
 };
 class 
class ReysProtocol {
  private:
  bool isHandshake;
//  Packet dataPacket;

  public:

  ReysProtocol() {
  isHandshake = false;
//  dataPacket = new Packet() 
  }

  void start() {
      if(isHandshake) {
        Serial.println("Handshake with relay node completed");
      }  

      else {
        byte relayNodePacket = Serial.read();

        if(relayNodePacket == SYN)
          Serial.write(ACK);

        if(relayNodePacket == ACK)
          isHandshake = true;
      }  
  }

};

byte dataPacket[PACKET_SIZE];
int sequenceNumber = 0;
ReysProtocol* protocol;

//dummy variables 
//bool condition = false;

void create_data_packet(float data) {
	//TODO: Need to define code over here
}


void send_dummy_packet() {

  Serial.write("100");
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

//void handshake_mechanism(bool isHandShakeComplete) {
//	int receivedData = Serial.read();
//	bool completionStatus = false;
//
//	//If received packet is 'S', create ACK packet and send to the relay node
//	if(receivedData == 83) 
//		Serial.write(ACK);
//	
//	//If received packet is 'A' set complettionStatus to True
//	if(receivedData == 65)
//		completionStatus = true;
//	
//	
//	return completionStatus;
//}

void setup(void) {
  Serial.begin(115200);
  protocol = new ReysProtocol();
}

void loop(void) {
    protocol->start();
//    delay(1000);
}
