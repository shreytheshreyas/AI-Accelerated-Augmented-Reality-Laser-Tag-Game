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
        0: "D0:39:72:BF:CA:D4",
        1: "D0:39:72:BF:C3:8F",
        2: "D0:39:72:BF:C8:D8",
        3: "",
        4: "",
        5: "",
        6: "D0:39:72:BF:C8:89",
        7: "D0:39:72:BF:C8:D7",
        8: "6C:79:B8:D3:6A:A3"
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
    syncStatusFlags = [False] * NUM_OF_BEETLES 
    ackStatusFlags = [False] * NUM_OF_BEETLES 
    dataAckStatusFlags = [False] * NUM_OF_BEETLES 
    dataNackStatusFlags = [False] * NUM_OF_BEETLES
    
    connectionStatusLock = threading.Lock()
    syncStatusLock = threading.Lock()
    ackStatusLock = threading.Lock()
    dataAckStatusLock = threading.Lock()   
    dataNackStatusLock = threading.Lock()

    #METHODS ASSOCIATED WITH  BUFFER
    @classmethod
    def set_connection_status(cls, beetle_id):
        cls.syncStatusLock.acquire()
        cls.syncStatusFlags[beetle_id] = True
        cls.syncStatusLock.release()

    @classmethod
    def clear_connection_status(cls, beetle_id):
        cls.syncStatusLock.acquire()
        cls.syncStausFlags[beetle_id] = False
        cls.syncStatusLock.release()

    @classmethod
    def get_connection_status(cls, beetle_id):
        return cls.syncStatusFlags[beetle_id]
 
    
    #METHODS ASSOCIATED WITH SYNC BUFFER
    @classmethod
    def set_sync_status(cls, beetle_id):
        cls.syncStatusLock.acquire()
        cls.syncStatusFlags[beetle_id] = True
        cls.syncStatusLock.release()

    @classmethod
    def clear_sync_status(cls, beetle_id):
        cls.syncStatusLock.acquire()
        cls.syncStausFlags[beetle_id] = False
        cls.syncStatusLock.release()

    @classmethod
    def get_sync_status(cls, beetle_id):
        return cls.syncStatusFlags[beetle_id]
    
    
    
    #METHODS ASSOCIATED WITH ACK BUFFER
    @classmethod
    def set_ack_status(cls, beetle_id):
        cls.ackStatusLock.acquire()
        cls.ackStausFlags[beetle_id] = True
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

    def check_packet(self, packetData):
        checksum = 0
        
        for idx in range(len(packetData) - 1):
            checksum = (checksum ^ packetData[idx]) & 0xFF

        return  packetData[len(packetData) - 1] == checksum

    def handleNotification(self, cHandle, data):
        self.receivingBuffer += data

        if len(self.receivingBuffer) == 1 and self.receivingBuffer.decode(encoding='ascii') == 'A':
            logging.info(f'The received information is as follows:\n')
            logging.info(self.receivingBuffer.decode(encoding='ascii'))
            logging.info(f'ACK received from beetle-{self.beetleId} successfully')
            self.receivingBuffer = b''

        elif len(self.receivingBuffer) >= 20:
            packetData = bytearray(self.receivingBuffer[:20])
            receivingBuffer = self.receivingBuffer[20:]
            
            sequenceNumber = struct.unpack('b', packetData[1:2])
            packetType = struct.unpack('b', packetData[2:3])
            actualCrcValue = struct.unpack('b', packetData[19:20])
            isPacketCorrect = self.check_packet(packetData)
            
            if packetType == GUN:
                print(f'RECEIVED GUN DATA FROM BEETLE- {self.beetleId}')
                gunData = struct.unpack('b', packetData[3:4])
                print(f'VALUE RETURNED BY GUN DATA = {gunData[0]}')
                print(f'Sequence number of packet = {sequenceNumber}')
                print(f'Packet type = {packetType}')
                print(f'Packet is not corrupted = {isPacketCorrect}\n')

        else: #Dealing with the case where data spans across multiple packets
            print('Packet is fragmented')
            pass



class BlunoDevice:
    def __init__(self, beetleId, macAddress):
        self.beetleId = beetleId
        self.macAddress = macAddress
        self.peripheral = None
        self.blutoothInterfaceHandler = None

    def establish_connection(self, text):
        try:
            self.peripheral = Peripheral(self.macAddress)
            self.bluetoothInterfaceHandler = BluetoothInterfaceHandler(self.beetleId, self.wasWirelessDisconnected)
            self.peripheral.withDelegate(self.bluetoothInterfaceHandler)  
            StatusManager.set_connection_status(self.beetleId)
            logging.info(f'Connection successfully established between the beetle-{self.beetleId} and relay node.')
        except Exception as e:
                logging.info(f'Could not connect to bluno device: {self.beetleId} due to the following exception.\n {e}')
    
    def transmit_packet(self, data):
        for characteristic in self.peripheral.getCharacteristics():
            characteristic.write(bytes(data,'ascii'), withResponse=False)

    def handshake_mechanism(self, isHandshakeCompleted):
        if StatusManager.get_connection_status(self.beetleId):
            self.transmit_packet(SYNC)
            waitForNotification(1.0) 

            if StatusManager.get_sync_status[self.beetleId]:
                self.trasmit_packet(ACK)
                StatusManager.set_ack_status(self.beetleId)
                isHandshakeCompleted = True 
                logging.info(f'Handshake Completed for beetle-{self.beetleId}')

        return isHandshakeCompleted
    
    def transmission_protocol(self,text):
        isHandshakeCompleted = False
        while True:
            try:
                if not isHandshakeCompleted:
                    if not StatusManager.get_connection_status(self.beetleId):
                        self.establish_connection(self.beetleId)
                    isHandshakeCompleted = self.handshake_mechanism(isHandshakeCompleted)
                else:
                    #regular data transfer
                    logging.info(f'{self.beetleID} -> regualar data transfer')
                    
            except KeyboardInterrupt:
                self.peripheral.disconnect()

            except (BTLEDisconnectError, AttributeError):
                logging.info(f'Beetle-{self.beetleId} been disconnected due to a significantly large distance from the relay node')
                logging.info(f'Attempting Reconnection')
                isHandshakeCompleted = False
                StatusManager.clear_connection_status(self.beetleId)
                StatusManager.clear_sync_status(self.beetleId)
                StatusManager.clear_ack_status(self.beetleId)
                StatusManager.clear_data_ack_status(self.beetleId)
                StatusManager.clear_data_nack_status(self.beetleID)

if __name__ == '__main__':
    
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")  
    #Player-1
    #beetle0 = BlunoDevice(PLAYER_1_GUN, MAC_ADDRESSES[PLAYER_1_GUN])
    #beetle1 = BlunoDevice(PLAYER_1_VEST, MAC_ADDRESSES[PLAYER_1_VEST])
    #beetle2 = BlunoDevice(PLAYER_1_MPU, MAC_ADDRESSES[PLAYER_1_MPU])
    
    #Player-2
    #beetle3 = BlunoDevice(PLAYER_2_GUN, MAC_ADDRESSES[PLAYER_2_GUN])
    #beetle4 = BlunoDevice(PLAYER_2_VEST, MAC_ADDRESSES[PLAYER_2_VEST])
    #beetle5 = BlunoDevice(PLAYER_2_MPU, MAC_ADDRESSES[PLAYER_2_MPU])
    
    #Testers
    beetle6 = BlunoDevice(TEST_GUN, MAC_ADDRESSES[TEST_GUN])
    beetle7 = BlunoDevice(TEST_VEST, MAC_ADDRESSES[TEST_VEST])
    beetle8 = BlunoDevice(TEST_MPU, MAC_ADDRESSES[TEST_MPU])
    
    logging.info('Instantiation of threads')
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(beetle6.transmission_protocol, ('beetle-6'))
        #executor.submit(beetle7.transmission_protocol, ('beetle-7'))
        #executor.submit(beetle8.transmission_protocol, ('beetle-8'))
