#
#define PAYLOAD_SIZE 7

uint8_t sequence_counter = 0;
//beetle_id = 1 //Player-1 Gun 
//beetle_id = 2 //Player-1 Vest
//beetle_id = 3 //Player-1 Wrist-band
//beetle_id = 4 //Player-2 Gun 
//beetle_id = 5 //Player-2 Vest 
//beetle_id = 6 //Player-2 Wrist-band

// # of Bytes per packet = 20
struct packet_data {
  String packet_type; // # of Bytes = 3 // If the string doesnt work, just change the implementation to numbers.
  uint8_t beetle_id; // # of Bytes = 1 // 
  uint8_t checksum;   // # of Bytes = 1
  uint16_t sequence_number; // # of Bytes = 1
  uint16_t payload[PAYLOAD_SIZE]; // # of Bytes = 14
};

//function to calcuate checksum 
uint8_t calculate_checksum(packet_data packet) {
  return 0;
  }
//function to create a packet 
packet_data create_packet(char packet_type[3], uint8_t beetle_id, uint16_t sequence_number, uint16_t payload[PAYLOAD_SIZE]) {

  packet_data beetle_packet = {
    .packet_type = packet_type, 
    .beetle_id = beetle_id, 
    .checksum = 0,
    .sequence_number = sequence_number
    };

  for (int i = 0; i < PAYLOAD_SIZE; i++) {
    beetle_packet.payload[i] = payload[i];
  }
  
  beetle_packet.checksum = calculate_checksum(beetle_packet);
  
  return beetle_packet;
}

void transmit_packet(packet_data beetle_packet) {

  //Implementation will have to changed for this later while integration and connecting to the beetle.,
  Serial.write((uint8_t*) &beetle_packet, sizeof(beetle_packet));
}
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

int counter = 0;
int previousTime = 0;
void loop() {
//  int currentTime = millis();
//  if (currentTime - previousTime > 1000) {
  Serial.write(counter);
  Serial.write('\n');
  counter = (counter + 1) % 122;
//  previousTime = millis();
  delay(500);
//  }
}
