#include <Wire.h>
#pragma pack(1)

#define LABEL "shield"

//Defining important constants
#define PACKET_SIZE 20
#define SENSOR_DATA 20
#define SAMPLE_POINT_ID 14
#define DATA_RATE 115200
#define TIMEOUT 50
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
int dummy1 = 0;
int dummy2 = 0;
uint8_t samplePointNumber = 0;

typedef union intDataByteFormat {
  byte byteValue[2];
  int intValue;
} intByteData;

typedef struct imuData {
  int linear_accel_x;
  int linear_accel_y;
  int linear_accel_z;
  int gyro_accel_x;
  int gyro_accel_y;
  int gyro_accel_z;
};

//Class definition for protocol
class Protocol {
  private:
    int sensorDataIdx;
    int sequenceNumber;
    int previousTime;
    int currentTime;
    imuData sensorData[SENSOR_DATA];
    imuData sensorDataTemp;
    byte packet[PACKET_SIZE];

  public:
    Protocol();
    int calculate_checksum(void);
    void clear_serial_buffer(void);
    void floatToByteConverter(void);
    void get_sensor_data(void);
    void initialize_imu_data(float, float, float, float, float, float);
    void initialize_packet_data(void);
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

  for (int idx = 0; idx < SENSOR_DATA; idx++)
    this->sensorData[idx] = (imuData) {
    0, 0, 0, 0, 0, 0
  };//In acutal implementation will change to 0

  for (int idx = 0; idx < 13; idx++)
    this->packet[idx] = 0;
}

int Protocol::calculate_checksum(void) {
  byte checksum = 0;

  for (int idx = 0; idx < PACKET_SIZE - 1; idx++)
    checksum ^= this->packet[idx];

  //  Serial.println(checksum);
  return checksum;
}

void Protocol::clear_serial_buffer() {
  while (Serial.available())
    byte dummy = Serial.read();
}


void Protocol::initialize_imu_data(float linear_accel_x, float linear_accel_y, float linear_accel_z, float gyro_accel_x, float gyro_accel_y, float gyro_accel_z) {
    this->sensorDataTemp.linear_accel_x = int16_t(linear_accel_x * 1024);
    this->sensorDataTemp.linear_accel_y = int16_t(linear_accel_y * 1024);
    this->sensorDataTemp.linear_accel_z = int16_t(linear_accel_z * 1024);
    this->sensorDataTemp.gyro_accel_x = int16_t(gyro_accel_x * 128);
    this->sensorDataTemp.gyro_accel_y = int16_t(gyro_accel_y * 128);
    this->sensorDataTemp.gyro_accel_z = int16_t(gyro_accel_z * 128);
}

void Protocol::initialize_packet_data() {
  //  union integerDataByteFormat samplePointNumberByteValue;
  //  samplePointNumberByteValue.integerValue = samplePointNumber;
  this->packet[0] = this->sequenceNumber;
  this->packet[1] = IMU_DATA;
  this->initialize_packet_accel_data();
  this->initialize_packet_gyro_data();
  this->packet[PACKET_SIZE - 1] = calculate_checksum();
}

void Protocol::initialize_packet_accel_data(void) {

  //Initializing packet with Linear Acceleration X-componenet Data
  this->packet[2] = byte((this->sensorDataTemp.linear_accel_x >> 8));
  this->packet[3] = byte((this->sensorDataTemp.linear_accel_x));

  //Initializing packet with Linear Acceleration Y-componenet Data
  this->packet[4] = byte((this->sensorDataTemp.linear_accel_y >> 8));
  this->packet[5] = byte((this->sensorDataTemp.linear_accel_y));

  //Initializing packet with Linear Acceleration Z-componenet Data
  this->packet[6] = byte((this->sensorDataTemp.linear_accel_z >> 8));
  this->packet[7] = byte((this->sensorDataTemp.linear_accel_z));
}

void Protocol::initialize_packet_gyro_data(void) {
  //  union intDataByteFormat vectorComponentX;
  //  union intDataByteFormat vectorComponentY;
  //  union intDataByteFormat vectorComponentZ;

  //  vectorComponentX.intValue = int(this->sensorDataTemp.gyro_accel_x * 128);
  //  vectorComponentY.intValue = int(this->sensorDataTemp.gyro_accel_y * 128);
  //  vectorComponentZ.intValue = int(this->sensorDataTemp.gyro_accel_z * 128);

  //  vectorComponentX.intValue = int(this->sensorDataTemp.gyro_accel_x);
  //  vectorComponentY.intValue = int(this->sensorDataTemp.gyro_accel_y);
  //  vectorComponentZ.intValue = int(this->sensorDataTemp.gyro_accel_z);
  //  Serial.print("Gyro-X = ");
  //  Serial.println(vectorComponentX.intValue);
  //  Serial.print("Gyro-Y = ");
  //  Serial.println(vectorComponentY.intValue);
  //  Serial.print("Gyro-Z = ");
  //  Serial.println(vectorComponentZ.intValue);

  //Initializing packet with Gyro Acceleration X-componenet Data
  this->packet[8] = byte((this->sensorDataTemp.gyro_accel_x >> 8));
  this->packet[9] = byte((this->sensorDataTemp.gyro_accel_x));

  //Initializing packet with Gyro Acceleration Y-componenet Data
  this->packet[10] = byte((this->sensorDataTemp.gyro_accel_y >> 8));
  this->packet[11] = byte((this->sensorDataTemp.gyro_accel_y));

  //Initializing packet with Gyro Acceleration Z-componenet Data
  this->packet[12] = byte((this->sensorDataTemp.gyro_accel_z >> 8));
  this->packet[13] = byte((this->sensorDataTemp.gyro_accel_z));
}


void Protocol::start_communication() {
  currentTime = millis();


  byte receivedData = Serial.read();

  switch (receivedData) {
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
      dummy1++;
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
  //  delay(20);
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


  communicationProtocol->initialize_imu_data(AccX, AccY, AccZ, GyroX, GyroY, GyroZ);
  communicationProtocol->initialize_packet_data();
  communicationProtocol->start_communication();
  communicationProtocol->clear_serial_buffer();
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
