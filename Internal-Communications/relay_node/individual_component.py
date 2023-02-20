from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError, ADDR_TYPE_RANDOM
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from os import system
import threading 
import logging
import time 
import struct


#Respond Message Buffer size
NUM_OF_BEETLES =  9 #Need to update to 6 to accomodate two players
DATA_BUFFER_SIZE = 20

#BLUNO ID's for the respective players 
PLAYER_1_GUN = 0
PLAYER_1_VEST = 1
PLAYER_1_MPU = 2
PLAYER_2_GUN = 3
PLAYER_2_VEST = 4
PLAYER_2_MPU = 5
TEST_GUN = 6
TEST_VEST = 7
TEST_MPU = 8

#Constants for packet types 
SYNC = 'S' #Packet type for handshake. 
RST = 'R' #For reseting beetle state
ACK = 'A' #Packet type for SYN-acknowledgment. 
DATA_ACK = 'D' #Packet type for data-acknowledgment
DATA_NACK = 'N' #Packet type for data-nagative-acknowledgment
IMU = 'I' #The ASCII code associated with I is 73
GUN = 'G' #The ASCII code associated with G is 71
VEST = 'V' #The ASCII code associated with V is 86


MAC_ADDRESSES = {
        0: 'D0:39:72:BF:CA:D4',
        1: 'D0:39:72:BF:C3:8F',
        2: 'D0:39:72:BF:C8:D8',
        3: 'a',
        4: 'a',
        5: 'a',
        6: 'D0:39:72:BF:C8:89',
        7: 'D0:39:72:BF:C8:D7',
        8: '6C:79:B8:D3:6A:A3'
}

class StatisticsManager:
    beetlesKbps = [0] * NUM_OF_BEETLES
    fragmentedPacketCounter = 0

'''
BufferManager DOCUMENTATION
'''
class BufferManager:
    relayNodeBuffer = Queue(DATA_BUFFER_SIZE)
    
    @classmethod
    def insertDataValue(cls, beetle_id, dataValue):
        pass

    @classmethod 
    def transferDataValue(cls):
        pass


'''
StatusManager DOCUMENTATION
This is primarly used to access the following class level variables 

1. connectionStatusFlags - Boolean list 
    -This variable represent a list which specifies the connection
     state with an associated beetle is either on or off.
    
    -The index position is associated with a beetle's ID. This means 
     connectionStatusFlags[3] represents the connection status of 
     beetle-3

    - The boolean values are used to represent state:
        * True -> beetle is connected to relay node
        * False -> beetle is not connected to relay node
    
    - Following are the locks associated with this list object:
        * connectionStatusLock 

2. syncStatusFlags - Boolean list 
    -This variable represent a list which specifies the 
     synchronisaion/hello state with an associated beetle.
    
    -The index position is associated with a beetle's ID. This means 
     connectionStatusFlags[3] represents the connection status of 
     beetle-3

    - The boolean values are used to represent state:
        * True -> beetle has received SYN packet and is synchronized with 
                  relay node.
        
        * False -> beetle has not received SYN packet or has disconnected 
                   from relay node.
    
    - Following are the locks associated with this list object:
        * syncStatusLock 

2. ackStatusFlags - Boolean list 
    -This variable represent a list which mentions that the relay node 
     has sent an acknowledgment for the ack received from the beetle
     during synchronization.
    
    -The index position is associated with a beetle's ID. This means 
     connectionStatusFlags[3] represents the connection status of 
     beetle-3

    - The boolean values are used to represent state:
        * True -> relay node has sent final ack packet for three-way-handshake.
        
        * False -> beetle has not sent final ack for three-way-handshake.
    
    - Following are the locks associated with this list object:
        * ackStatusLock 

3. dataAckStatusFlags - Boolean list 
    -This variable represent a list which mentions that the relay node 
     has received data correctly from the transmitter and receiver sensors
     successfully.
    
    -The index position is associated with a beetle's ID. This means 
     connectionStatusFlags[3] represents the connection status of 
     beetle-3

    - The boolean values are used to represent state:
        * True -> received data successfully.
        
        * False -> has not received anything from sensor.
    
    - Following are the locks associated with this list object:
        * dataAckStatusLock 

4. dataNackStatusFlags - Boolean list 
    -This variable represent a list which mentions that the relay node 
     has received data in a corrupted format from the transmitterand 
     receiver sensors.
    
    -The index position is associated with a beetle's ID. This means 
     connectionStatusFlags[3] represents the connection status of 
     beetle-3

    - The boolean values are used to represent state:
        * True -> received data unsuccessfully.
        
        * False -> has not received anything from sensor.
    
    - Following are the locks associated with this list object:
        * dataNackStatusLock 

'''
class StatusManager:
    
    connectionStatusFlags = [False] * NUM_OF_BEETLES   
    resetStatusFlags = [False] * NUM_OF_BEETLES
    syncStatusFlags = [False] * NUM_OF_BEETLES 
    ackStatusFlags = [False] * NUM_OF_BEETLES 
    dataAckStatusFlags = [False] * NUM_OF_BEETLES 
    dataNackStatusFlags = [False] * NUM_OF_BEETLES
    
    connectionStatusLock = threading.Lock()
    resetStatusLock = threading.Lock()
    syncStatusLock = threading.Lock()
    ackStatusLock = threading.Lock()
    dataAckStatusLock = threading.Lock()   
    dataNackStatusLock = threading.Lock()

    #METHODS ASSOCIATED WITH CONNECTION BUFFER
    @classmethod
    def set_connection_status(cls, beetle_id):
        cls.syncStatusLock.acquire()
        cls.connectionStatusFlags[beetle_id] = True
        cls.syncStatusLock.release()

    @classmethod
    def clear_connection_status(cls, beetle_id):
        cls.syncStatusLock.acquire()
        cls.connectionStatusFlags[beetle_id] = False
        cls.syncStatusLock.release()

    @classmethod
    def get_connection_status(cls, beetle_id):
        return cls.connectionStatusFlags[beetle_id]
 
    #METHODS ASSOCIATED WITH RESET BUFFER
    @classmethod
    def set_reset_status(cls, beetle_id):
        cls.resetStatusLock.acquire()
        cls.resetStatusFlags[beetle_id] = True
        cls.resetStatusLock.release()

    @classmethod
    def clear_reset_status(cls, beetle_id):
        cls.resetStatusLock.acquire()
        cls.resetStatusFlags[beetle_id] = False
        cls.resetStatusLock.release()

    @classmethod
    def get_reset_status(cls, beetle_id):
        return cls.resetStatusFlags[beetle_id]
 
    
    #METHODS ASSOCIATED WITH SYNC BUFFER
    @classmethod
    def set_sync_status(cls, beetle_id):
        cls.syncStatusLock.acquire()
        cls.syncStatusFlags[beetle_id] = True
        cls.syncStatusLock.release()

    @classmethod
    def clear_sync_status(cls, beetle_id):
        cls.syncStatusLock.acquire()
        cls.syncStatusFlags[beetle_id] = False
        cls.syncStatusLock.release()

    @classmethod
    def get_sync_status(cls, beetle_id):
        return cls.syncStatusFlags[beetle_id]
    
    
    
    #METHODS ASSOCIATED WITH ACK BUFFER
    @classmethod
    def set_ack_status(cls, beetle_id):
        cls.ackStatusLock.acquire()
        cls.ackStatusFlags[beetle_id] = True
        cls.ackStatusLock.release()

    @classmethod
    def clear_ack_status(cls, beetle_id):
        cls.ackStatusLock.acquire()
        cls.ackStatusFlags[beetle_id] = False
        cls.ackStatusLock.release()

    @classmethod
    def get_ack_status(cls, beetle_id):
        return cls.ackStatusFlags[beetle_id]
    
    
    #METHODS ASSOCIATED WITH DATA-ACK BUFFER
    @classmethod
    def set_data_ack_status(cls, beetle_id):
        cls.dataAckStatusLock.acquire()
        cls.dataAckStatusFlags[beetle_id] = True
        cls.dataAckStatusLock.release() 

    @classmethod
    def clear_data_ack_status(cls, beetle_id):
        cls.dataAckStatusLock.acquire()
        cls.dataAckStatusFlags[beetle_id] = False
        cls.dataAckStatusLock.release() 
    
    @classmethod
    def get_data_ack_status(cls, beetle_id):
        return cls.dataAckStatusFlags[beetle_id]
    
    
    #METHODS ASSOCIATED WITH DATA-NACK BUFFER
    @classmethod
    def set_data_nack_status(cls, beetle_id):
       cls.dataNackStatusFlags[beetle_id] = True
 
    @classmethod
    def clear_data_nack_status(cls, beetle_id):
        cls.dataNackStatusLock.acquire()
        cls.dataNackStatusFlags[beetle_id] = False
        cls.dataNackStatusLock.release() 

    @classmethod
    def get_data_nack_status(cls, beetle_id):
        return cls.dataNackStatusFlags[beetle_id]
   

class BluetoothInterfaceHandler(DefaultDelegate):
    def __init__(self, beetleId):
        DefaultDelegate.__init__(self)
        self.beetleId = beetleId
        self.receivingBuffer = b'' 

    def verify_checksum(self, packetData):
        checksum = 0        
        for idx in range(len(packetData) - 1):
            checksum = (checksum ^ packetData[idx])
        return  packetData[19] == checksum

    def handleNotification(self, cHandle, data):
        system('clear')
        print('\r')
        try:
            self.receivingBuffer += data 
            if len(self.receivingBuffer) == 1: 
                if self.receivingBuffer.decode('ascii') == RST:
                    logging.info(f'The received information from {self.beetleId} is as follows:\n')
                    logging.info(self.receivingBuffer.decode(encoding='ascii'))
                    logging.info(f'RST received from beetle-{self.beetleId} successfully')
                    StatusManager.set_reset_status(self.beetleId)
                    
                if self.receivingBuffer.decode('ascii') == ACK:
                    logging.info(f'The received information from {self.beetleId} is as follows:\n')
                    logging.info(self.receivingBuffer.decode(encoding='ascii'))
                    logging.info(f'ACK received from beetle-{self.beetleId} successfully')
                    StatusManager.set_sync_status(self.beetleId)
                
                self.receivingBuffer = b''
        
            elif len(self.receivingBuffer) >= 20:
                packetData = self.receivingBuffer[0:20]
                self.receivingBuffer = self.receivingBuffer[20:]
                isPacketCorrect = self.verify_checksum(packetData)
                #logging.info(f'checksum = {isPacketCorrect}')
                #packetType = struct.unpack('b', packetData[1:2])[0]
                #gunData = struct.unpack('b', packetData[2:3])[0]
                #sequenceNumber = struct.unpack('b', packetData[0:1])[0] 
                #logging.info(f'packetType = {packetType}')
                #logging.info(f'gunData = {gunData}')
                #logging.info(f'sequenceNumber = {sequenceNumber}')

                if isPacketCorrect == True:
                    sequenceNumber = struct.unpack('b', packetData[0:1])[0]
                    packetType = struct.unpack('b', packetData[1:2])[0]
                    #logging.info(f'packetType = {packetType}')
                    if chr(packetType) == GUN:
                        print('##########RECEIVED-GUN-DATA###############')
                        gunData = struct.unpack('B', packetData[2:3])[0]
                        logging.info(f'packet-type = {packetType}')
                        logging.info(f'sequence-number = {sequenceNumber}')
                        logging.info(f'value received from gun = {gunData}')
                        logging.info(f'is the packet corrupted = {not isPacketCorrect}')
                  
                    if chr(packetType) == VEST:
                        print('##########RECEIVED-VEST-DATA###############')
                        vestData = struct.unpack('B', packetData[2:3])[0]
                        logging.info(f'packet-type = {chr(packetType)}')
                        logging.info(f'sequence-number = {sequenceNumber}')
                        logging.info(f'value received from vest = {vestData}')
                        logging.info(f'is the packet corrupted = {not isPacketCorrect}')

                    if chr(packetType) == IMU: 
                        print('##########RECEIVED-IMU-DATA###############')
                        imuDataLinearAccelX = struct.unpack('B', packetData[2:3])[0]
                        imuDataLinearAccelY = struct.unpack('B', packetData[3:4])[0]
                        imuDataLinearAccelZ = struct.unpack('B', packetData[4:5])[0]
                        imuDataGyroAccelX = struct.unpack('B', packetData[5:6])[0]
                        imuDataGyroAccelY = struct.unpack('B', packetData[6:7])[0]
                        imuDataGyroAccelZ = struct.unpack('B', packetData[7:8])[0]
                        logging.info(f'packet-type = {packetType}')
                        logging.info(f'sequence-number = {sequenceNumber}')
                        logging.info(f'Linear-Acceleration-X = {imuDataLinearAccelX}')
                        logging.info(f'Linear-Acceleration-Y = {imuDataLinearAccelY}')
                        logging.info(f'Linear-Acceleration-Z = {imuDataLinearAccelZ}')
                        logging.info(f'Gyro-Acceleration-Y = {imuDataGyroAccelX}')
                        logging.info(f'Gyro-Acceleration-Z = {imuDataGyroAccelY}')
                        logging.info(f'Gyro-Acceleration-Z = {imuDataGyroAccelZ}')
                        logging.info(f'is the packet corrupted = {not isPacketCorrect}')
                    
                    StatusManager.set_data_ack_status(self.beetleId)

                else:
                    logging.info('Packet is corrupted!')
                    StatusManager.set_data_nack_status(self.beetleId)

            else:
                self.receivingBuffer = b''
                print('Packet is fragmented')
                pass 
        except Exception as e: 
            logging.info(f'handleNotfications: Something Went wrong. please see the exception message below:\n {e}')

class BlunoDevice:
    def __init__(self, beetleId, macAddress):
        self.beetleId = beetleId
        self.macAddress = macAddress
        self.peripheral = None
        self.blutoothInterfaceHandler = None
        #self.isHandshakeCompleted = False
    
    def transmit_packet(self, data):
        try:
            for characteristic in self.peripheral.getCharacteristics():
                characteristic.write(bytes(data, 'ascii'), withResponse=False)
        except (BTLEDisconnectError, AttributeError):
            pass
        except Exception as e:
            logging.info(f'Some thing went wrong while trying to transmit packet to {self.beetleId}, please refer to the following exception:\n {e}')
        
    
    def establish_connection(self): 
        try:
            self.peripheral = Peripheral(self.macAddress)
            self.bluetoothInterfaceHandler = BluetoothInterfaceHandler(self.beetleId)
            self.peripheral.withDelegate(self.bluetoothInterfaceHandler)
            StatusManager.set_connection_status(self.beetleId)
            logging.info(f'Connection successfully established between the beetle-{self.beetleId} and relay node.') 
        except Exception as e:
            logging.info(f'Could not connect to bluno device: {self.beetleId} due to the following exception.\n {e}')

    def reset_controller(self):
        try:
            self.transmit_packet(RST)
            self.peripheral.waitForNotifications(1.0)
        except (BTLEDisconnectError, AttributeError):
            pass
        except Exception as e:
            logging.info(f'Some thing went wrong while trying to reset {self.beetleId}, please refer to the following exception:\n {e}')
        
    def handshake_mechanism(self, isHandshakeCompleted):
        if StatusManager.get_connection_status(self.beetleId):
            self.transmit_packet(SYNC)
            self.peripheral.waitForNotifications(1.0) 

            if StatusManager.get_sync_status(self.beetleId):
                self.transmit_packet(ACK)
                StatusManager.set_ack_status(self.beetleId)
                isHandshakeCompleted = True 
                logging.info(f'Handshake Completed for beetle-{self.beetleId}\n')
        return isHandshakeCompleted
    
    def transmission_protocol(self):
        isHandshakeCompleted = False
        
        while True:
            try:
                if not isHandshakeCompleted:
                    if not StatusManager.get_connection_status(self.beetleId):
                        self.establish_connection()
                    
                    if not StatusManager.get_reset_status(self.beetleId):
                        self.reset_controller()

                    isHandshakeCompleted = self.handshake_mechanism(isHandshakeCompleted)
                    logging.info(isHandshakeCompleted)
                else:
                    #regular data transfer
                    #logging.info(f'{self.beetleId} - regular data transfer')

                    #logging.info('Before waiting for notification')
                    self.peripheral.waitForNotifications(3.0)
                    #logging.info('After waiting for notification')

                    if StatusManager.get_data_ack_status(self.beetleId):
                        self.transmit_packet(DATA_ACK)
                        StatusManager.clear_data_ack_status(self.beetleId)

                    if StatusManager.get_data_nack_status(self.beetleId):
                        self.transmit_packet(DATA_NACK)
                        StatusManager.clear_data_nack_status(self.beetleId)
                    
                    print('\n')
                    #self.peripheral.disconnect()
                    #logging.info(f'beetle-{self.beetleId} is disconnected')
                    #logging.info(f'beetle-{self.beetleId}: regualar data transfer')
                     
            
            except KeyboardInterrupt:
                logging('Program terminated due a keyboard interrupt')
                self.peripheral.disconnect() 
            
            #except Exception as e: 
                #logging.info(f'something went wrong due to the following error: \n {e}')

            except (BTLEDisconnectError, AttributeError):
                logging.info(f'Beetle-{self.beetleId} been disconnected due to a significantly large distance from the relay node')
                logging.info(f'Attempting Reconnection')
                isHandshakeCompleted = False
                StatusManager.clear_connection_status(self.beetleId)
                StatusManager.clear_reset_status(self.beetleId)
                StatusManager.clear_sync_status(self.beetleId)
                StatusManager.clear_ack_status(self.beetleId)
                StatusManager.clear_data_ack_status(self.beetleId)
                StatusManager.clear_data_nack_status(self.beetleId)
                pass            
            
if __name__ == '__main__':
    
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")  
    
    #Player-1
    beetle0 = BlunoDevice(PLAYER_1_GUN, MAC_ADDRESSES[PLAYER_1_GUN])
    beetle1 = BlunoDevice(PLAYER_1_VEST, MAC_ADDRESSES[PLAYER_1_VEST])
    beetle2 = BlunoDevice(PLAYER_1_MPU, MAC_ADDRESSES[PLAYER_1_MPU])
    
    #Player-2
    beetle3 = BlunoDevice(PLAYER_2_GUN, MAC_ADDRESSES[PLAYER_2_GUN])
    beetle4 = BlunoDevice(PLAYER_2_VEST, MAC_ADDRESSES[PLAYER_2_VEST])
    beetle5 = BlunoDevice(PLAYER_2_MPU, MAC_ADDRESSES[PLAYER_2_MPU])
    
    #Testers
    beetle6 = BlunoDevice(TEST_GUN, MAC_ADDRESSES[TEST_GUN])
    beetle7 = BlunoDevice(TEST_VEST, MAC_ADDRESSES[TEST_VEST])
    beetle8 = BlunoDevice(TEST_MPU, MAC_ADDRESSES[TEST_MPU])
    
    #Instantiation of Threads 
    logging.info('Instantiation of threads')
    #beetleThread0 = threading.Thread(target=beetle0.transmission_protocol, args=())
    #beetleThread1 = threading.Thread(target=beetle1.transmission_protocol, args=()) 
    #beetleThread2 = threading.Thread(target=beetle2.transmission_, args=())
    #beetleThread3 = threading.Thread(target=beetle3.establish_connection, args=())
    #beetleThread4 = threading.Thread(target=beetle4.establish_connection, args=())
    #beetleThread5 = threading.Thread(target=beetle5.establish_connection, args=())
    beetleThread6 = threading.Thread(target=beetle6.transmission_protocol, args=())
    beetleThread7 = threading.Thread(target=beetle7.transmission_protocol, args=())
    beetleThread8 = threading.Thread(target=beetle8.transmission_protocol, args=())
    
    #Starting beetle Threads
    #beetleThread0.start()
    #beetleThread1.start()
    #beetleThread2.start()
    #beetleThread3.start()
    #beetleThread4.start()
    #beetleThread5.start()
    beetleThread6.start()
    beetleThread7.start()
    beetleThread8.start()

    #Terminating beetle Threads
    #beetleThread0.join()
    #beetleThread1.join()
    #beetleThread2.join()
    #beetleThread3.join()
    #beetleThread4.join()
    #beetleThread5.join()
    beetleThread6.join()
    beetleThread7.join()
    beetleThread8.join()

