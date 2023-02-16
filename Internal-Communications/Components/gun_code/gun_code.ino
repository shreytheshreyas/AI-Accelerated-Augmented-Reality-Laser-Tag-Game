//Defining important constants
#define PACKET_SIZE 20
#define SENSOR_DATA 20
#define DATA_RATE 115200

//Defining packet types
#define SYNC 'S'
#define ACK 'A'
#define GUN_DATA 'G'
#define DATA_ACK 'D'
#define DATA_NACK 'N'
#define RST 'R'
#define RST_ACK 'r'

//Class definition for protocol
class Protocol {
  private:
    int sensorDataIdx;
    int sequenceNumber;
    int sensorData[SENSOR_DATA];
    uint8_t packet[PACKET_SIZE];

  public:
    Protocol();
    int calculate_checksum(void);
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

  for(int idx = 0; idx < SENSOR_DATA; idx++)
    this->sensorData[idx] = 10; //In acutal implementation will change to 0

  for(int idx = 0; idx < PACKET_SIZE; idx++)
    this->sensorData[idx] = 0;
}

int Protocol::calculate_checksum(void) {
  uint8_t checksum = 0;
  
  for(int idx = 0; idx < PACKET_SIZE-1; idx++)
    checksum ^= this->packet[idx];

  return checksum;
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
  if (Serial.available()) {
    uint8_t receivedData = Serial.read();

    if (hasHandshakeEnded) {
      
      if (receivedData == DATA_ACK) {
        this->sequenceNumber++;
        this->sensorDataIdx = (this->sensorDataIdx + 1) % 20; 
      }

      if (receivedData == DATA_NACK){  
      //TODO: Might need some code over here to integration phase
      }

      Serial.write((uint8_t*) &packet, sizeof(packet));
    }

    switch(receivedData) {
      case SYNC: hasHandshakeStarted = true;
                 hasHandshakeEnded = false;
                 Serial.write(ACK);
                 break;

      case ACK: hasHandshakeStarted = false;
                hasHandshakeEnded = true;
                break;

      case RST: hasHandshakeStarted = false;
                hasHandshakeEnded = false;
                Serial.write(RST_ACK);
                break;
    }
  }
  
}
void setup() {
  Serial.begin(DATA_RATE);
  hasHandshakeStarted = false;
  hasHandshakeEnded = false;
  communicationProtocol = new Protocol();
}

void loop() {
  communicationProtocol->get_sensor_data();
  communicationProtocol->start_communication();
}
