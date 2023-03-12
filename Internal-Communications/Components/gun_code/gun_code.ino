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

#define DECODE_NEC

const int buttonPin = 2;    // Button at pin D2
const int IR_SEND_PIN = 3;  // IR transmitter at pin D3
const int buzzerPin = 5;    //buzzer at pin D5
int buttonState = 0;

const uint16_t PLAYER_1_ADDRESS = 0x0102;
const uint16_t PLAYER_2_ADDRESS = 0x0105;
const uint8_t command = 0x01; //1 for player 1
uint8_t repeats = 1;
uint8_t shotCounter = 0;
unsigned long sensorDelayStartTime = 0;
byte sendDataPacket = false;

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
    void initialize_packet_data(int16_t);
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

void Protocol::initialize_packet_data(int16_t buttonStateData) {
  this->packet[0] = this->sequenceNumber;
  this->packet[1] = GUN_DATA;
  this->packet[2] = byte('1');
  this->packet[4] = this->sensorData[sensorDataIdx];
  this->packet[PACKET_SIZE - 1] = this->calculate_checksum(); 
}

void Protocol::start_communication() {
   this->currentTime = millis();

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

  if ( (hasHandshakeEnded) && (currentTime -  previousTime > TIMEOUT) &&  receivedData != ACK && sendDataPacket) { 
    Serial.write((byte*)&packet, sizeof(packet));
    sendDataPacket = false;
    this->previousTime = this->currentTime;
  }

  this->clear_serial_buffer();
}

void sensorDelay(long interval) {
 unsigned long currentMillis = millis();

 while(currentMillis - sensorDelayStartTime < interval)
    currentMillis = millis();
 
}

void outOfAmmoTune() {
  tone(buzzerPin,NOTE_D1,100);
  sensorDelayStartTime = millis();
  sensorDelay(100); //replace with custom delay
  tone(buzzerPin,NOTE_E1,100);
}


void setup() {
  Serial.begin(DATA_RATE);
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(buzzerPin, OUTPUT);
  IrSender.begin(IR_SEND_PIN);  //start sending pin
  hasHandshakeStarted = false;
  hasHandshakeEnded = false;
  communicationProtocol = new Protocol();
}

void loop() {
//  Serial.flush();
  buttonState = digitalRead(buttonPin);
//  Serial.println(buttonState);

  if (buttonState == 0) {
    shotCounter += 1;
    sendDataPacket = true;
    switch (shotCounter) {
      case 1:
      IrSender.sendNEC(PLAYER_1_ADDRESS, command, repeats);
      Serial.println("signal has been sent");
      Serial.println(buttonState);
      tone(buzzerPin,NOTE_C6,100);
      sensorDelayStartTime = millis();
      sensorDelay(500);
      break;

      case 2:
      IrSender.sendNEC(PLAYER_1_ADDRESS, command, repeats);
      Serial.println("signal has been sent");
      Serial.println(buttonState);
      tone(buzzerPin,NOTE_D6  ,100);
      sensorDelayStartTime = millis();
      sensorDelay(500);
      break;

      case 3:
      IrSender.sendNEC(PLAYER_1_ADDRESS, command, repeats);
      Serial.println("signal has been sent");
      Serial.println(buttonState);
      tone(buzzerPin,NOTE_E6,100);
      sensorDelayStartTime = millis();
      sensorDelay(500);
      break;

      case 4:
      IrSender.sendNEC(PLAYER_1_ADDRESS, command, repeats);
      Serial.println("signal has been sent");
      Serial.println(buttonState);
      tone(buzzerPin,NOTE_F6,100);
      sensorDelayStartTime = millis();
      sensorDelay(500);
      break;

      case 5:
      IrSender.sendNEC(PLAYER_1_ADDRESS, command, repeats);
      Serial.println("signal has been sent");
      Serial.println(buttonState);
      tone(buzzerPin,NOTE_G6,100);
      sensorDelayStartTime = millis();
      sensorDelay(500);
      break;

      case 6:
      IrSender.sendNEC(PLAYER_1_ADDRESS, command, repeats);
      Serial.println("signal has been sent");
      Serial.println(buttonState);
      tone(buzzerPin,NOTE_A6,100);
      sensorDelayStartTime = millis();
      sensorDelay(500);
      break;

      // case 7:
      // IrSender.sendNEC(PLAYER_1_ADDRESS, command, repeats);
      // Serial.println("signal has been sent");
      // Serial.println(buttonState);
      // tone(buzzerPin,NOTE_B6 ,100);
      // delay(500);
      // break;

      default:
      Serial.println("out of ammo");
      outOfAmmoTune();
      sensorDelayStartTime = millis();
      sensorDelay(500);
      break;
   }
  }

  communicationProtocol->initialize_packet_data(buttonState);
  communicationProtocol->start_communication();
//  communicationProtocol->clear_serial_buffer();
}
