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

const uint16_t PLAYER_1_ADDRESS = '1';
const uint16_t PLAYER_2_ADDRESS = '2';
const uint8_t command = 'G'; //1 for player 1

uint8_t ammoStatus = 0;
uint8_t repeats = 1;
uint8_t bulletCount = 6;
unsigned long sensorDelayStartTime = 0;
byte sendDataPacket = false;

// Test Timings
unsigned long testCurr;
unsigned long testPrev;

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
    void send_data(void);
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

    for(int idx = 0; idx < 5; idx++)
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
    this->packet[2] = bulletCount;
    this->packet[4] = this->sensorData[sensorDataIdx];
    this->packet[PACKET_SIZE - 1] = this->calculate_checksum();
}

void Protocol::start_communication() {

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

    case RST:
        hasHandshakeStarted = false;
        hasHandshakeEnded = false;
//                this->clear_serial_buffer();
        Serial.write(RST);
        break;

    case FIN:
        //Some code to handle this scenario
        break;
    }
}

void Protocol::send_data() {
    this->currentTime = millis();
    if ( (hasHandshakeEnded) && (this->currentTime -  this->previousTime > TIMEOUT) && sendDataPacket) {
        Serial.write((byte*)&packet, sizeof(packet));
        sendDataPacket = false;
        this->previousTime = this->currentTime;
    }
    /* byte dataAck = Serial.read(); */
    /* if (dataAck != ACK) { */
    /*     // Do something here */
    /* } */
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
    if (!hasHandshakeEnded) {
        communicationProtocol->start_communication();
        return;
    }

    if (Serial.available()) {
        int data = Serial.read();
        //Serial.print(data);
        if ((char)data == RST) {
            //Serial.print("bytes match");
            //Serial.write('M');
            hasHandshakeStarted = false;
            hasHandshakeEnded = false;
            Serial.write(RST);
            return;
        }

        sensorDelayStartTime = millis();
        sensorDelay(50);
        int newBulletCount = data;
        if (bulletCount != newBulletCount) {
            bulletCount = newBulletCount;
            tone(buzzerPin,NOTE_C6,100);
        }
    }

    buttonState = digitalRead(buttonPin);

    if (buttonState == 0) {
        sendDataPacket = true;
        ammoStatus = 1;

        if (bulletCount == 6) {
            tone(buzzerPin,NOTE_C6,100);
        } else if (bulletCount == 5) {
            tone(buzzerPin,NOTE_D6,100);
        } else if (bulletCount == 4) {
            tone(buzzerPin,NOTE_E6,100);
        } else if (bulletCount == 3) {
            tone(buzzerPin,NOTE_F6,100);
        } else if (bulletCount == 2) {
            tone(buzzerPin,NOTE_G6,100);
        } else if (bulletCount == 1) {
            tone(buzzerPin,NOTE_A6,100);
        }

        if (bulletCount > 0) {
            IrSender.sendNEC(PLAYER_1_ADDRESS, command, repeats);
        } else {
            outOfAmmoTune();
            ammoStatus = 13;

        }
        communicationProtocol->initialize_packet_data(buttonState);
        communicationProtocol->send_data();

        if (bulletCount > 0) {
            bulletCount -= 1;
        }

        sensorDelayStartTime = millis();
        sensorDelay(1000);
    }

//  communicationProtocol->clear_serial_buffer();
}
