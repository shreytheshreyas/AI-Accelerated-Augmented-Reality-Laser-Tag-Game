#include "CRC8.h"

#define DATA_RATE 115200 //Defining datarate to be 115200 baud
#define PACKET_SIZE 20 //Defining packet size to be 20 bytes

#define BEETLE_DEVICE 0 //Need to change this for each and every beetle

//Packet Indices 
#define BEETLE_ID 0
#define SEQUENCE_NUMBER 1
#define PACKET_TYPE 2

//BEETLE_IDs
#define PLAYER_1_TRANSMITTER 0
#define PLAYER_1_RECEIVER 1
#define PLAYER_1_IMU 2
#define PLAYER_2_TRANSMITTER 3
#define PLAYER_2_RECEIVER 4
#define PLAYER_2_IMU 5
#define TEST_TRANSMITTER 6
#define TEST_RECEIVER 7
#define TEST_IMU 8

//PACKET TYPES
#define GUN 'G'
#define VEST 'V'
#define IMU 'I'
#define ACK 'A' //The letter 'A' corresponds to the ASCII code 65
#define NACK 'N'
#define SYN 'S'
#define DATA 'D' //Data response from the relay node 
CRC8 crc;
byte dataPacket[PACKET_SIZE];
int sequenceNumber = 0;

//timer values for time out functionality of protocol
bool isTimerStarted  = true; //In reality the default value will be false and will be updated by an interrupt, when the gun trigger is pressed
bool canSendData = true; // state will be changed by an interrrupt
long timeoutValue = 100;
long transmissionStartTime = 0;

typedef struct PacketStructure {
  uint8_t beetleId;
  uint8_t sequenceNumber;
  uint8_t packetType;
  uint8_t payload_1;
  uint8_t payload_2;
  uint8_t payload_3;
  uint8_t payload_4;
  uint8_t payload_5;
  uint8_t payload_6;
  uint8_t payload_7;
  uint8_t payload_8;
  uint8_t payload_9;
  uint8_t payload_10;
  uint8_t payload_11;
  uint8_t payload_12;
  uint8_t payload_13;
  uint8_t payload_14;
  uint8_t payload_15;
  uint8_t payload_16;
  uint8_t crcValue;
};

class GunPacketData{
  private:
    PacketStructure packet;
    int address;
    int command;
  public:

    GunPacketData() {
      address = 0;
      command = 0;
    }
    
    void setGunData() {
      packet.beetleId = (uint8_t) TEST_TRANSMITTER;
      packet.sequenceNumber = (uint8_t) sequenceNumber;
      packet.packetType = (uint8_t) GUN;
      packet.payload_1 = (uint8_t) 0;
      packet.payload_2 = (uint8_t) 0;
      packet.payload_3 = (uint8_t) 0;
      packet.payload_4 = (uint8_t) 0;
      packet.payload_5 = (uint8_t) 0;
      packet.payload_6 = (uint8_t) 0;
      packet.payload_7 = (uint8_t) 0;
      packet.payload_8 = (uint8_t) 0;
      packet.payload_9 = (uint8_t) 0;
      packet.payload_10 = (uint8_t) 0;
      packet.payload_11 = (uint8_t) 0;
      packet.payload_12 = (uint8_t) 0;
      packet.payload_13 = (uint8_t) 0;
      packet.payload_14 = (uint8_t) 0;
      packet.payload_15 = (uint8_t) 0;
      packet.payload_16 = (uint8_t) 67;

      //calcualting crc8 value 
      crc.add(packet.beetleId);
      crc.add(packet.sequenceNumber);
      crc.add(packet.packetType);
      crc.add(packet.payload_1);
      crc.add(packet.payload_2);
      crc.add(packet.payload_3);
      crc.add(packet.payload_4);
      crc.add(packet.payload_5);
      crc.add(packet.payload_6);
      crc.add(packet.payload_7);
      crc.add(packet.payload_8);
      crc.add(packet.payload_9);
      crc.add(packet.payload_10);
      crc.add(packet.payload_11);
      crc.add(packet.payload_12);
      crc.add(packet.payload_13);
      crc.add(packet.payload_14);
      crc.add(packet.payload_15);
      crc.add(packet.payload_16);

      //storing crc value in last byte of packet
      packet.crcValue = crc.getCRC();

      //Updating Sequence after storing packet details 
      sequenceNumber++;
      sequenceNumber %= 255;
      }

      void transmitPacket() {
        Serial.write((uint8_t*)&packet, sizeof(packet));
//        Serial.write(0x01);
      }
};




class ReysProtocol {
  private:
  bool handshakeStart;
  bool handshakeEnd;
  GunPacketData *packet;

  public:

  ReysProtocol() {
    handshakeStart = false;
    handshakeEnd = false;
    packet = new GunPacketData();
  }

  
  void start() {
    if (Serial.available()) {
      uint8_t receivedData = Serial.read();
      switch(receivedData) {
        case SYN: handshakeStart = true;
                  handshakeEnd = false;
                  Serial.write(ACK);
                  break;
  
        case ACK:   handshakeStart = false;
                    handshakeEnd = true;
      }
    }
  
    if (handshakeEnd) {
  //     Serial.print(ACK);
      packet->setGunData();
      packet->transmitPacket();
    }
  }
};


ReysProtocol* protocol;
//bool handshakeStart = false;
//bool handshakeEnd = false;
void setup() {
  Serial.begin(115200);
  protocol = new ReysProtocol();
}

void loop() {

  protocol->start();

//  if (Serial.available()) {
//    uint8_t receivedData = Serial.read();
//    switch(receivedData) {
//      case SYN: handshakeStart = true;
//                handshakeEnd = false;
//                Serial.write(ACK);
//                break;
//
//      case ACK:   handshakeStart = false;
//                  handshakeEnd = true;
//    }
//  }
//
//  if (handshakeEnd) {
//     Serial.print(2.98);
//  }
}
