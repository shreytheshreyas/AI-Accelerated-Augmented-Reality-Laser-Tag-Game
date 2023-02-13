#include <IRremote.hpp>

#define DECODE_NEC 

const int buttonPin = 2; // Button at pin D2
const int IR_SEND_PIN = 3; // IR transmitter at pin D3
const int buzzerPin = 5; //buzzer at pin D5

int buttonState = 0; 

const uint16_t PLAYER_1_ADDRESS = 0x0102;
const uint16_t PLAYER_2_ADDRESS = 0x0103;
const uint8_t command = 0x01;
uint8_t repeats = 1;
uint8_t shotCounter = 0;


void setup() {
  // put your setup code here, to run once:

  pinMode(buttonPin,INPUT_PULLUP);
  pinMode(buzzerPin,OUTPUT);
  Serial.begin(19200);
  IrSender.begin(IR_SEND_PIN);  //start sending pin
}

void loop() {
  // put your main code here, to run repeatedly:
  buttonState = digitalRead(buttonPin);
  Serial.println(buttonState);

  if (buttonState ==0){
    shotCounter +=1;
    if (shotCounter <= 7) {
    IrSender.sendNEC(PLAYER_1_ADDRESS,command,repeats);
    Serial.println("signal has been sent");
    Serial.println(buttonState);
    tone(buzzerPin,3000,100);
    delay(1000);

    }
    else if (shotCounter == 8) {
      Serial.println("out of ammo");
      tone(buzzerPin,2000,100);
    }
  }
  Serial.println(shotCounter);
}
