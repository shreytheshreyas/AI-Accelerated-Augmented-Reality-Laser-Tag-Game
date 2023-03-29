#include <IRremote.hpp>
#include <TM1637Display.h>
#include "pitches.h"

//Defining Necessary Constants for IR Receiver
#define DECODE_NEC
#define CLK 4
#define DIO 2
#define IR_RCV_PIN 3
#define BUZZER_PIN 5

//Defining important constants
#define PACKET_SIZE 20
#define SENSOR_DATA 20
#define DATA_RATE 115200
#define TIMEOUT 50
#define IR_RATIO 32699

#define INIT_HEALTH 100

//Defining packet types
#define SYNC 'S'
#define ACK 'A'
#define VEST_DATA 'V'
#define DATA_ACK 'D'
#define DATA_NACK 'N'
#define RST 'R'
#define RST_ACK 'r'
#define FIN 'F'

// Create a display object of type TM1637Display
TM1637Display display = TM1637Display(CLK, DIO);

const uint16_t PLAYER_1_ADDRESS = 0x0102; //Address for Player 1's Shot
const uint16_t PLAYER_2_ADDRESS = 0x0105; //Address for Player 2's Shot
uint8_t shotID;
uint8_t health = INIT_HEALTH;
uint8_t lifeStatus = 0;
bool sendData = false;
unsigned long sensorDelayStartTime = 0;
int i;

const uint8_t DEAD[] = {
    SEG_A | SEG_B | SEG_C | SEG_D | SEG_E,           // D
    SEG_A | SEG_D | SEG_E | SEG_F | SEG_G,           // E
    SEG_A | SEG_B | SEG_C | SEG_E | SEG_F | SEG_G,   // A
    SEG_A | SEG_B | SEG_C | SEG_D | SEG_E            // D
};

int melody[] = {

    NOTE_C4, NOTE_G3, NOTE_G3, NOTE_A3, NOTE_G3, 0, NOTE_B3, NOTE_C4
};

// note durations: 4 = quarter note, 8 = eighth note, etc.:
int noteDurations[] = {

    4, 8, 8, 4, 4, 4, 4, 4
};


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
    this->packet[1] = VEST_DATA;
    this->packet[2] = health;
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
        Serial.write(RST);
        break;

    case FIN:
        //Some code to handle this scenario
        break;
    }
}

void Protocol::send_data() {
    this->currentTime = millis();
    if ( (hasHandshakeEnded) && (this->currentTime -  this->previousTime > TIMEOUT) && sendData) {
        Serial.write((byte*)&packet, sizeof(packet));
        sendData= false;
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
void deadTune() {
    for (int thisNote = 0; thisNote < 8; thisNote++) {
        int noteDuration = 1000 / noteDurations[thisNote];
        tone(BUZZER_PIN, melody[thisNote], noteDuration);
        int pauseBetweenNotes = noteDuration * 1.30;
        sensorDelayStartTime = millis();
        sensorDelay(pauseBetweenNotes);
        noTone(8);
    }
}

void setup() {
    Serial.begin(DATA_RATE);
    pinMode(BUZZER_PIN,OUTPUT);
    display.setBrightness(5);
    display.showNumberDec(health);
    IrReceiver.begin(IR_RCV_PIN); //Start receiving
    hasHandshakeStarted = false;
    hasHandshakeEnded = false;
    communicationProtocol = new Protocol();
}

void loop() {
    if (!hasHandshakeEnded) {
        communicationProtocol->start_communication();
        return;
    }
    if (IrReceiver.decode()) {
        /* sensorDelay(); */
        /* sensorDelayStartTime = millis(); */
        if (IrReceiver.decodedIRData.command == 'G') {
            sendData = true;
            communicationProtocol->initialize_packet_data();
            communicationProtocol->send_data();

            health -= 10;
            tone(BUZZER_PIN,5000,100);
            display.showNumberDec(health);

            sendData = true;
            if (health == 0) {
                display.setSegments(DEAD);
                deadTune();
                sensorDelayStartTime = millis();
                sensorDelay(1000);
                health = 100;
                display.showNumberDec(health);
            }
        }
        IrReceiver.begin(IR_RCV_PIN); //continue receiving IR signals
    }
    if (Serial.available()) {
        int data = Serial.read();
        if ((char)data == '\n') {
            return;
        }
        if ((char)data == RST) {
            hasHandshakeStarted = false;
            hasHandshakeEnded = false;
            Serial.write(RST);
            return;
        }

        if (data == 125) {
            data = 130;
        }
        if (health != data) {
            tone(BUZZER_PIN,5000,100);
            health = data;
            display.showNumberDec(health);
        }
        sensorDelayStartTime = millis();
        sensorDelay(200);
        IrReceiver.begin(IR_RCV_PIN); // CANNOT REMOVE
    }
}
