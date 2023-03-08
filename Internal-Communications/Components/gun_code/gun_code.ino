#include <IRremote.hpp>
#include "pitches.h"

//Defining important constants
#define PACKET_SIZE 20
#define SENSOR_DATA 20
#define DATA_RATE 115200
#define TIMEOUT 50
//Defining packet types
#define SYNC 'S'
#define ACK 'A'
#define GUN_DATA 'G'
#define DATA_ACK 'D'
#define DATA_NACK 'N'
#define RST 'R'
#define RST_ACK 'r'
#define FIN 'F'

//Class definition for protocol
class Protocol {
  private:
    int sensorDataIdx;
    int sequenceNumber;
    int previousTime;
    int currentTime;
    int sensorData[SENSOR_DATA];
    byte packet[PACKET_SIZE];

  public:
    Protocol();
    int calculate_checksum(void);
    void clear_serial_buffer(void);
    void get_sensor_data(void);
    void initialize_packet_data(void);
    void start_communication(void);
};

//global variable declarations 
bool hasHandshakeStarted;
bool hasHandshakeEnded;
Protocol* communicationProtocol;


//function definitions 
Protocol::Protocol() {
  this->sensorDataIdx = 0; 
  this->sequenceNumber = 0;
  this->previousTime = 0;
  this->currentTime = 0;
  
  for(int idx = 0; idx < SENSOR_DATA; idx++)
    this->sensorData[idx] = 10 + idx; //In acutal implementation will change to 0

  for(int idx = 0; idx < PACKET_SIZE; idx++)
    this->packet[idx] = 0;
}

int Protocol::calculate_checksum(void) {
  uint8_t checksum = 0;
  
  for(int idx = 0; idx < PACKET_SIZE-1; idx++)
    checksum ^= this->packet[idx];

  return checksum;
}

void Protocol::clear_serial_buffer() {
  while(Serial.available()) 
    byte dummy = Serial.read();
}

void Protocol::get_sensor_data() {
  return;
}

void Protocol::initialize_packet_data() {
  this->packet[0] = this->sequenceNumber;
  this->packet[1] = GUN_DATA;
  this->packet[2] = this->sensorData[sensorDataIdx];
  this->packet[PACKET_SIZE - 1] = this->calculate_checksum(); 
}

void Protocol::start_communication() {
   currentTime = millis();

//    if (!Serial.available())
//      return;
      
    byte receivedData = Serial.read();

    switch(receivedData) {
      case SYNC: 
                 hasHandshakeStarted = true;
                 hasHandshakeEnded = false;
                 Serial.write(ACK);
                 break;

      case ACK: 
                hasHandshakeStarted = false;
                hasHandshakeEnded = true;
                break;

      case DATA_ACK: 
                this->sequenceNumber++;
                this->sensorDataIdx = (this->sensorDataIdx + 1) % 20;
                
                break;

      case DATA_NACK:
                //Some code to handle this scenario
                break;
                
      case RST: hasHandshakeStarted = false;
                hasHandshakeEnded = false;
//                this->clear_serial_buffer();
                Serial.write(RST);
                break;

      case FIN: 
                //Some code to handle this scenario
                break;
    }

  if ( (hasHandshakeEnded) && (currentTime -  previousTime > TIMEOUT) &&  receivedData != ACK) { 
    Serial.write((byte*)&packet, sizeof(packet));
    previousTime = currentTime;
  }

  this->clear_serial_buffer();
}

void setup() {
  Serial.begin(DATA_RATE);
  hasHandshakeStarted = false;
  hasHandshakeEnded = false;
  communicationProtocol = new Protocol();
}

void loop() {
//  Serial.flush();
  communicationProtocol->initialize_packet_data();
  communicationProtocol->start_communication();
//  communicationProtocol->clear_serial_buffer();
}
