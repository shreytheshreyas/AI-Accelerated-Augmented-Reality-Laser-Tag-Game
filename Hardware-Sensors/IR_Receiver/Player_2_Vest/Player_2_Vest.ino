#include <IRremote.hpp>
#include <TM1637Display.h>
#include "pitches.h"

#define DECODE_NEC
#define CLK 4
#define DIO 2
#define IR_RCV_PIN 3
#define BUZZER_PIN 5

// Create a display object of type TM1637Display
TM1637Display display = TM1637Display(CLK, DIO);

const uint16_t PLAYER_1_ADDRESS = 0x0102; //Address for Player 1's Shot
const uint16_t PLAYER_2_ADDRESS = 0x0105; //Address for Player 2's Shot
bool isShot = false;  //To indicate if hit is registered
uint8_t shotID;
uint8_t shotCounter = 0;
uint8_t health = 100;

const uint8_t DEAD[] = {
  SEG_A | SEG_B | SEG_C | SEG_D | SEG_E,   // D
  SEG_A | SEG_D | SEG_E | SEG_F | SEG_G,   // E
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

void setup() {
  // put your setup code here, to run once:
  pinMode(BUZZER_PIN,OUTPUT);  
  display.setBrightness(5);
  display.showNumberDec(health);
  Serial.begin(19200);
  IrReceiver.begin(IR_RCV_PIN); //Start receiving
}

void deadTune(){
  for (int thisNote = 0; thisNote < 8; thisNote++) {
    int noteDuration = 1000 / noteDurations[thisNote];
    tone(BUZZER_PIN, melody[thisNote], noteDuration);
    int pauseBetweenNotes = noteDuration * 1.30;
    delay(pauseBetweenNotes);
    noTone(8);
  }
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
       
      if (isShot == true && health == 0) {
        display.setSegments(DEAD);
        deadTune();
        health = 0;
      } 
      else if (isShot == true){
        shotCounter += 1;
        health = 100 - shotCounter*10;
        tone(BUZZER_PIN,5000,100);
        isShot = false;

        if (health == 0) {
          display.setSegments(DEAD);
          deadTune();
          delay(100);
          health = 100;
          display.setshowNumberDec(health);
        }
        else {
          display.showNumberDec(health);
          delay(100);
        }

      }       
    }
    IrReceiver.begin(IR_RCV_PIN); //continue receiving IR signals
    // IrReceiver.resume();
  }
}
