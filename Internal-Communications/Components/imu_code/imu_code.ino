#include <Wire.h>
#define LABEL "shield"

//Defining important constants
#define PACKET_SIZE 20
#define SENSOR_DATA 20
#define SAMPLE_POINT_ID 14
#define DATA_RATE 115200
#define TIMEOUT 5000
//#define TIMEOUT 1000
//#define TIMEOUT 5000

//Defining packet types
#define SYNC 'S'
#define ACK 'A'
#define IMU_DATA 'I'
#define DATA_ACK 'D'
#define DATA_NACK 'N'
#define RST 'R'
#define RST_ACK 'r'
#define FIN 'F'

//Defining Packet initializing constant
#define ACC_INIT 0
#define GYRO_INIT 1
#define ROT_FORCE_INIT 2

//Defining index constants for imu packet initialization
#define FIRST_FLOAT_VALUE 2
#define SECOND_FLOAT_VALUE 6
#define THIRD_FLOAT_VALUE 10
#define VALUES_IDX_TERMINATION 14

const int MPU = 0x68; // MPU6050 I2C address
float AccX, AccY, AccZ;
float GyroX, GyroY, GyroZ;
float accAngleX, accAngleY, gyroAngleX, gyroAngleY, gyroAngleZ;
float AccErrorX, AccErrorY, GyroErrorX, GyroErrorY, GyroErrorZ;
float elapsedTime, currentTime, previousTime;
int c = 0;
int newDataCounter = 0;
bool transmitLinearAccelData = true;
bool transmitGyroAccelData = false;
uint8_t samplePointNumber = 0;

typedef union floatDataByteFormat{
 byte byteValue[4];
 float floatValue;  
} floatByteData;

typedef struct imuData {
  float linear_accel_x;
  float linear_accel_y;
  float linear_accel_z;
  float gyro_accel_x;
  float gyro_accel_y;
  float gyro_accel_z;
};

//Class definition for protocol
class Protocol {
  private:
    int sensorDataIdx;
    int sequenceNumber;
    int previousTime;
    int currentTime;
    int samplePointId;
    imuData sensorData[SENSOR_DATA];
    imuData sensorDataTemp;
    byte packet[PACKET_SIZE];

  public:
    Protocol();
    int calculate_checksum(void);
    void clear_serial_buffer(void);
    void floatToByteConverter(void);
    void get_sensor_data(void);
    void initialize_imu_data(float,float,float,float,float,float);
    void initialize_packet_data(int);
    void initialize_packet_accel_data(void);
    void initialize_packet_gyro_data(void);
    void initialize_packet_rotational_force_data(void);
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
    this->sensorData[idx] = (imuData) {0, 0, 0, 0, 0, 0};//In acutal implementation will change to 0

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


void Protocol::initialize_imu_data(float linear_accel_x, float linear_accel_y, float linear_accel_z, float gyro_accel_x, float gyro_accel_y, float gyro_accel_z) {
  this->sensorDataTemp.linear_accel_x = linear_accel_x;
  this->sensorDataTemp.linear_accel_y = linear_accel_y;
  this->sensorDataTemp.linear_accel_z = linear_accel_z;
  this->sensorDataTemp.gyro_accel_x = gyro_accel_x;
  this->sensorDataTemp.gyro_accel_y = gyro_accel_y;
  this->sensorDataTemp.gyro_accel_z = gyro_accel_z;

  Serial.println("Before Conversion to float-byte form");
  Serial.print(this->sensorDataTemp.linear_accel_x);
  Serial.print(",");
  Serial.print(this->sensorDataTemp.linear_accel_y);
  Serial.print(",");
  Serial.print(this->sensorDataTemp.linear_accel_z);
  Serial.print(",");
  Serial.print(this->sensorDataTemp.gyro_accel_x);
  Serial.print(",");
  Serial.print(this->sensorDataTemp.gyro_accel_y);
  Serial.print(",");
  Serial.println(this->sensorDataTemp.gyro_accel_z);

  Serial.println("After conversion to float-byte form");
}
void Protocol::initialize_packet_data(int newDataCounter) {
//  union integerDataByteFormat samplePointNumberByteValue;
//  samplePointNumberByteValue.integerValue = samplePointNumber;
  this->packet[0] = this->sequenceNumber;
  this->packet[1] = IMU_DATA;

  switch (newDataCounter) {
    case ACC_INIT: this->initialize_packet_accel_data();
                    break;

    case GYRO_INIT: this->initialize_packet_gyro_data();
                    break;
  }
  
  this->packet[SAMPLE_POINT_ID] = this->samplePointId;
  this->packet[PACKET_SIZE - 1] = this->calculate_checksum(); 
}

void Protocol::initialize_packet_accel_data(void) {
  union floatDataByteFormat vectorComponentX;
  union floatDataByteFormat vectorComponentY;
  union floatDataByteFormat vectorComponentZ;

  vectorComponentX.floatValue = this->sensorDataTemp.linear_accel_x;
  vectorComponentY.floatValue = this->sensorDataTemp.linear_accel_y;
  vectorComponentZ.floatValue = this->sensorDataTemp.linear_accel_z;
  Serial.print("Linear-X = ");
  Serial.println(vectorComponentX.floatValue);
  Serial.print("Linear-Y = ");
  Serial.println(vectorComponentY.floatValue);
  Serial.print("Linear-Z = ");
  Serial.println(vectorComponentZ.floatValue);
  
  for (int i = 2; i < 6; i++) {
    this->packet[i] = vectorComponentX.byteValue[i - 2];
  }

  for(int i = 6; i < 10; i++) {
    this->packet[i] = vectorComponentY.byteValue[i - 6];
  }

  for(int i = 10; i < 14; i++) {
    this->packet[i] = vectorComponentZ.byteValue[i - 10];
  }
} 

void Protocol::initialize_packet_gyro_data(void) {
  union floatDataByteFormat vectorComponentX;
  union floatDataByteFormat vectorComponentY;
  union floatDataByteFormat vectorComponentZ;

  vectorComponentX.floatValue = this->sensorDataTemp.gyro_accel_x;
  vectorComponentY.floatValue = this->sensorDataTemp.gyro_accel_y;
  vectorComponentZ.floatValue = this->sensorDataTemp.gyro_accel_z;
  Serial.print("Gyro-X = ");
  Serial.println(vectorComponentX.floatValue);
  Serial.print("Gyro-Y = ");
  Serial.println(vectorComponentY.floatValue);
  Serial.print("Gyro-Z = ");
  Serial.println(vectorComponentZ.floatValue);
  
  for (int i = 2; i < 6; i++) {
    this->packet[i] = vectorComponentX.byteValue[i - 2];
  }

  for(int i = 6; i < 10; i++) {
    this->packet[i] = vectorComponentY.byteValue[i - 6];
  }

  for(int i = 10; i < 14; i++) {
    this->packet[i] = vectorComponentZ.byteValue[i - 10];
  }
}


void Protocol::start_communication() {
   currentTime = millis();

      
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
                if (newDataCounter == 0)
                  this->samplePointId++;
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

//  this->clear_serial_buffer();
}

void setup() {
  Serial.begin(DATA_RATE);
  hasHandshakeStarted = false;
  hasHandshakeEnded = false;
  communicationProtocol = new Protocol();

  Wire.begin();                      // Initialize comunication
  Wire.beginTransmission(MPU);       // Start communication with MPU6050 // MPU=0x68
  Wire.write(0x6B);                  // Talk to the register 6B
  Wire.write(0x00);                  // Make reset - place a 0 into the 6B register
  Wire.endTransmission(true);        //end the transmission

    // Call this function if you need to get the IMU error values for your module
  calculate_IMU_error();
  delay(20);
}

void loop() {
  
    // === Read acceleromter data === //
  Wire.beginTransmission(MPU);
  Wire.write(0x3B); // Start with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6, true); // Read 6 registers total, each axis value is stored in 2 registers
  //For a range of +-2g, we need to divide the raw values by 16384, according to the datasheet
  AccX = (Wire.read() << 8 | Wire.read()) / 16384.0; // X-axis value
  AccY = (Wire.read() << 8 | Wire.read()) / 16384.0; // Y-axis value
  AccZ = (Wire.read() << 8 | Wire.read()) / 16384.0; // Z-axis value

  // === Read gyroscope data === //
  previousTime = currentTime;        // Previous time is stored before the actual time read
  currentTime = millis();            // Current time actual time read
  elapsedTime = (currentTime - previousTime) / 1000; // Divide by 1000 to get seconds
  Wire.beginTransmission(MPU);
  Wire.write(0x43); // Gyro data first register address 0x43
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6, true); // Read 4 registers total, each axis value is stored in 2 registers
  GyroX = (Wire.read() << 8 | Wire.read()) / 131.0; // For a 250deg/s range we have to divide first the raw value by 131.0, according to the datasheet
  GyroY = (Wire.read() << 8 | Wire.read()) / 131.0;
  GyroZ = (Wire.read() << 8 | Wire.read()) / 131.0;
  // Correct the outputs with the calculated error values
  GyroX = GyroX - GyroErrorX; // GyroErrorX ~(-0.56)
  GyroY = GyroY - GyroErrorY; // GyroErrorY ~(2)
  GyroZ = GyroZ - GyroErrorZ; // GyroErrorZ ~ (-0.8)

  if (newDataCounter == 0)
    communicationProtocol->initialize_imu_data(AccX, AccY, AccZ, GyroX, GyroY, GyroZ);
    
  communicationProtocol->initialize_packet_data(newDataCounter);
  communicationProtocol->start_communication();
//  communicationProtocol->clear_serial_buffer();
  newDataCounter = (newDataCounter + 1) % 2;
}

void calculate_IMU_error() {
  // We can call this funtion in the setup section to calculate the accelerometer and gyro data error. From here we will get the error values used in the above equations printed on the Serial Monitor.
  // Note that we should place the IMU flat in order to get the proper values, so that we then can the correct values
  // Read accelerometer values 200 times
  while (c < 200) {
    Wire.beginTransmission(MPU);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, 6, true);
    AccX = (Wire.read() << 8 | Wire.read()) / 16384.0 ;
    AccY = (Wire.read() << 8 | Wire.read()) / 16384.0 ;
    AccZ = (Wire.read() << 8 | Wire.read()) / 16384.0 ;
    // Sum all readings
    AccErrorX = AccErrorX + ((atan((AccY) / sqrt(pow((AccX), 2) + pow((AccZ), 2))) * 180 / PI));
    AccErrorY = AccErrorY + ((atan(-1 * (AccX) / sqrt(pow((AccY), 2) + pow((AccZ), 2))) * 180 / PI));
    c++;
  }
  //Divide the sum by 200 to get the error value
  AccErrorX = AccErrorX / 200;
  AccErrorY = AccErrorY / 200;
  c = 0;
  // Read gyro values 200 times
  while (c < 200) {
    Wire.beginTransmission(MPU);
    Wire.write(0x43);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, 6, true);
    GyroX = Wire.read() << 8 | Wire.read();
    GyroY = Wire.read() << 8 | Wire.read();
    GyroZ = Wire.read() << 8 | Wire.read();
    // Sum all readings
    GyroErrorX = GyroErrorX + (GyroX / 131.0);
    GyroErrorY = GyroErrorY + (GyroY / 131.0);
    GyroErrorZ = GyroErrorZ + (GyroZ / 131.0);
    c++;
  }
  //Divide the sum by 200 to get the error value
  GyroErrorX = GyroErrorX / 200;
  GyroErrorY = GyroErrorY / 200;
  GyroErrorZ = GyroErrorZ / 200;
}
