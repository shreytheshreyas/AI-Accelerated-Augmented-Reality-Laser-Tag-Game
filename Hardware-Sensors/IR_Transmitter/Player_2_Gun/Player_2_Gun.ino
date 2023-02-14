#include <IRremote.hpp>
#include "pitches.h"

#define DECODE_NEC

const int buttonPin = 2;    // Button at pin D2
const int IR_SEND_PIN = 3;  // IR transmitter at pin D3
const int buzzerPin = 5;    //buzzer at pin D5

int buttonState = 0;

const uint16_t PLAYER_1_ADDRESS = 0x0102;
const uint16_t PLAYER_2_ADDRESS = 0x0105;
const uint8_t command = 0x02;   //2 for player 2
uint8_t repeats = 1;
uint8_t shotCounter = 0;

void setup() {
  // put your setup code here, to run once:

  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(buzzerPin, OUTPUT);
  Serial.begin(19200);
  IrSender.begin(IR_SEND_PIN);  //start sending pin
}

void outOfAmmoTune() {
  tone(buzzerPin,NOTE_D1,100);
  delay(100);
  tone(buzzerPin,NOTE_E1,100);
}

void loop() {
  // put your main code here, to run repeatedly:
  buttonState = digitalRead(buttonPin);
  Serial.println(buttonState);

  if (buttonState == 0) {
    shotCounter += 1;
    switch (shotCounter) {
      case 1:
      IrSender.sendNEC(PLAYER_2_ADDRESS, command, repeats);
      Serial.println("signal has been sent");
      Serial.println(buttonState);
      tone(buzzerPin,NOTE_C6,100);
      delay(500);
      break;

      case 2:
      IrSender.sendNEC(PLAYER_1_ADDRESS, command, repeats);
      Serial.println("signal has been sent");
      Serial.println(buttonState);
      tone(buzzerPin,NOTE_D6  ,100);
      delay(500);
      break;

      case 3:
      IrSender.sendNEC(PLAYER_1_ADDRESS, command, repeats);
      Serial.println("signal has been sent");
      Serial.println(buttonState);
      tone(buzzerPin,NOTE_E6,100);
      delay(500);
      break;

      case 4:
      IrSender.sendNEC(PLAYER_1_ADDRESS, command, repeats);
      Serial.println("signal has been sent");
      Serial.println(buttonState);
      tone(buzzerPin,NOTE_F6,100);
      delay(500);
      break;

      case 5:
      IrSender.sendNEC(PLAYER_1_ADDRESS, command, repeats);
      Serial.println("signal has been sent");
      Serial.println(buttonState);
      tone(buzzerPin,NOTE_G6,100);
      delay(500);
      break;

      case 6:
      IrSender.sendNEC(PLAYER_1_ADDRESS, command, repeats);
      Serial.println("signal has been sent");
      Serial.println(buttonState);
      tone(buzzerPin,NOTE_A6,100);
      delay(500);
      break;

      case 7:
      IrSender.sendNEC(PLAYER_1_ADDRESS, command, repeats);
      Serial.println("signal has been sent");
      Serial.println(buttonState);
      tone(buzzerPin,NOTE_B6 ,100);
      delay(500);
      break;

      default:
      Serial.println("out of ammo");
      outOfAmmoTune();
      delay(500);
      break;
  }
  } 
// Serial.println(shotCounter);
}
