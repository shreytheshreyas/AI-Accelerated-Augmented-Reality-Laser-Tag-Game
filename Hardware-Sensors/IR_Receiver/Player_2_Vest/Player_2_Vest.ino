#include <IRremote.hpp>

#define DECODE_NEC

const int IR_RCV_PIN = 3; // IR Receiver at pin D3
const int buzzerPin = 5; // Buzzer Pin at D5
const uint16_t PLAYER_1_ADDRESS = 0x0102; //Address for Player 1's Shot
const uint16_t PLAYER_2_ADDRESS = 0x0105; //Address for Player 2's Shot
bool isShot = false;  //To indicate if hit is registered
uint8_t shotID;

void setup() {
  // put your setup code here, to run once:
  pinMode(buzzerPin,OUTPUT);  
  Serial.begin(19200);
  IrReceiver.begin(IR_RCV_PIN); //Start receiving
}

void loop() {
  // put your main code here, to run repeatedly:

  if (IrReceiver.decode()) {  
    
    IrReceiver.printIRResultShort(&Serial);
    Serial.println(IrReceiver.decodedIRData.decodedRawData, HEX);
    
    if (IrReceiver.decodedIRData.command == 0x01) {   //if hit by player 1's shot
      isShot = true;
      shotID = IrReceiver.decodedIRData.command;  //shotID of the player that hit you
      Serial.println("Received signal");  //debug
    }

    if (isShot == true) { //trigger sound if shot is registered
    tone(buzzerPin,2000,100);
    isShot = false;
    delay(100);
    // Serial.println("test");
    }
    IrReceiver.begin(IR_RCV_PIN); //continue receiving IR signals
    // IrReceiver.resume();
  }
}
