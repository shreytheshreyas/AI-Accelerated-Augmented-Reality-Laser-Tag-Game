from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError, AssignedNumbers
from concurrent.futures import ThreadPoolExecutor
from crccheck.crc import Crc8
from queue import Queue
from os import system
import threading 
import logging
import time 
import struct


#Respond Message Buffer size
RESPONSE_BUFFER_SIZE = 9 #Need to update to 6 to accomodate two players
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
SYN = 'S' #Packet type for handshake. 
RST = 'R' #For reseting beetle state
ACK = 'A' #Packet type for SYN-acknowledgment. 
DATA-ACK = 'D' #Packet type for data-acknowledgment
DATA-NACK = 'N' #Packet type for data-nagative-acknowledgment
IMU = (73,) #The ASCII code associated with I is 73
GUN = (71,) #The ASCII code associated with G is 71
VEST = (86,) #The ASCII code associated with V is 86


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
    beetlesKbps = [0] * RESSPONSE_BUFFER_SIZE
    fragmentedPacketCounter = 0

class BufferManager:
    relayNodeBuffer = Queue(Data_Buffer_Size)
    
    @classmethod
    def insertDataValue(cls, beetle_id, dataValue):
        pass

    @classmethod 
    def transferDataValue(cls):
        pass

class StatusManager:
    syncStatusFlags = [False] * RESPONSE_BUFFER_SIZE #Used for synchronization 
    ackStatusFlags = [False] * RESPONSE_BUFFER_SIZE #Used for data transfer
    dataAckStatusFlags = [False] * RESPONSE_BUFFER_SIZE #Used for Data transfer
    dataNackStatusFlags = [False] * RESPONSE_BUFFER_SIZE #Used for Data transfer
    commonDataBuffer = Queue(DATA_BUFFER_SIZE) 
 
    #METHODS ASSOCIATED WITH SYNC BUFFER
    @classmethod
    def set_sync_status(cls, beetle_id):
       cls.syncStatusFlags[beetle_id] = True
    
    @classmethod
    def clear_sync_status(cls, beetle_id):
       cls.syncStausFlags[beetle_id] = False

    @classmethod
    def get_sync_status(cls, beetle_id):
        return cls.syncStatusFlags[beetle_id]
    
    
    #METHODS ASSOCIATED WITH ACK BUFFER
    @classmethod
    def set_ack_status(cls, beetle_id):
        cls.ackStausFlags[beetle_id] = True
    
    @classmethod
    def clear_ack_status(cls, beetle_id):
        cls.ackStatusFlags[beetle_id] = False

    @classmethod
    def get_ack_status(cls, beetle_id):
        return cls.ackStatusFlags[beetle_id]
    
    #METHODS ASSOCIATED WITH DATA-ACK BUFFER
    @classmethod
    def set_data_ack_status(cls, beetle_id):
        cls.dataAckStatusFlags[beetle_id] = True
    
    @classmethod
    def clear_data_ack_status(cls, beetle_id):
        cls.dataAckStatusFlags[beetle_id] = False

    @classmethod
    def get_data_ack_status(cls, beetle_id):
        return cls.dataAckStatusFlags[beetle_id]
    
    #METHODS ASSOCIATED WITH DATA-NACK BUFFER
    @classmethod
    def set_nack_status(cls, beetle_id):
       cls.dataNackStatusFlags[beetle_id] = True
 
    @classmethod
    def clear_nack_status(cls, beetle_id):
       cls.dataNackStatusFlags[beetle_id] = False

    @classmethod
    def get_nack_status(cls, beetle_id):
        return cls.dataNackStatusFlags[beetle_id]
   
    #METHODS ASSOCIATED WITH COMMON DATA BUFFER
    @classmethod
    def set_data_buffer(cls, beetle_id, data):
        logging.info(f'common-data-buffer being set by beetle-{beetle_id}')
        dataBufferLock.acquire()
        ####initialize commonDataBuffer with incomming data####
        dataBufferLock.release()
        pass
    
    @classmethod
    def get_data_buffer(cls):
        return cls.commonDataBuffer


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
        #print(self.receivingBuffer)
        #logging.info(f'inside handleNorifications function of beetle: {self.beetleId}')
        
        if self.wasWirelessDisconnected:
            self.receivingBuffer = b''
            self.wasWirelessDisconnected = False

        if len(self.receivingBuffer) == 1 and self.receivingBuffer.decode(encoding='ascii') == 'A':
            #Steps to deal with acknowledgement sent from the arduino 
            print(f'The Transmitted information is as follows:\n')
            print(self.receivingBuffer.decode(encoding='ascii'))
            logging.info(f'ACK received from beetle-{self.beetleId} successfully')
            #Flip flag bit associated with the beetleId to the set state so as to 
            #indicate that the synchronize packet has been acknowledged.
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
    def __init__(self, beetleId, macAddress, isARQ):
        self.beetleId = beetleId
        self.macAddress = macAddress
        self.peripheral = None
        self.blutoothInterfaceHandler = None
        self.wasWirelessDisconnected = False
        self.isARQ = isARQ ### No need to keep track of nagative-acknowledgement-buffer if this is set to false 

    def establish_connection(self, text):
        logging.info(f'In connect method {text}')
        while True:
            try: 
                self.peripheral = Peripheral(self.macAddress)
                #Peripheral(self.macAddress) 
                self.bluetoothInterfaceHandler = BluetoothInterfaceHandler(self.beetleId, self.wasWirelessDisconnected)
                self.peripheral.withDelegate(self.bluetoothInterfaceHandler)
                
                if self.wasWirelessDisconnected:
                    self.wasWirelessDisconnected = False

                #logging.info(self.peripheral.getCharacteristics())
                logging.info(f'Connection successfully established between the beetle-{self.beetleId} and relay node.')
                #self.peripheral.waitForNotifications(1)
                #logging.info('finished waiting for notifications')
                break
            except Exception as e:
                logging.info(f'Could not connect to bluno device: {self.beetleId} due to the following exception.\n {e}')
                break
    
    def transmit_data(self, data):
        try:
            for characteristic in self.peripheral.getCharacteristics():
                characteristic.write(bytes(data,'ascii'), withResponse=False)

        except Exception as e:
            logging.info(f'Something went wrong during the transmission process: \n {e}')
             
    def handshake_mechanism(self, isHandshakeCompleted):
        logging.info(f'Still in handshaking mechanism for beetle-{self.beetleId} and counter = {counter}')

        if not BufferManager.get_sync_status(self.beetleId): 
            #Step-1: Transmit synchronization packet from relay node 
            self.transmit_data(SYN)
            #Step-2: Set Timeout of ACK packet to be 2 seconds
            self.peripheral.waitForNotifications(2.0) 
            #logging.info('synchronization flag set in handshake mechanism')
                
        else:
            self.transmit_data(ACK)
            isHandshake = True 

        return isHandshakeCompleted
    
    def transmission_protocol(self,text):
        isHandshakeCompleted = False
        while True:
            try:
                #logging.info(f'HANDSHAKE-STATUS = {isHandshakeCompleted}') 
                if not isHandshakeCompleted:
                    #1. Connect/Reconnect to bettle 
                    self.establish_connection(self.beetleId)
                    #2. perform handshake mechanism 
                    isHandshakeCompleted = self.handshake_mechanism(isHandshakeCompleted)
                else:
                    #regular data transfer
                    self.peripheral.waitForNotifications(0.1)
                    
            except KeyboardInterrupt:
                self.peripheral.disconnect()
                print(f'Beetle-{self.beetleId} been disconnected due to a keyboard interrupt on the relay node')
        
            except (BTLEDisconnectError, AttributeError):
                print(f'Beetle-{self.beetleId} been disconnected due to a significantly large distance from the relay node')
                print(f'Attempting Reconnection')
                isHandshakeCompleted = False
                BufferManager.clear_sync_status(self.beetleId)
                
            except Exception as e:
                print(f'Something went wrong in protocol with beetle{self.beetleId}')
                print(f'Refer to the following exception below:\n {e}')
                self.peripheral.connect()
                isHandshakeCompleted = False

if __name__ == '__main__':
    
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")  
    #Player-1
    #beetle0 = BlunoDevice(PLAYER_1_GUN, MAC_ADDRESSES[PLAYER_1_GUN], True)
    #beetle1 = BlunoDevice(PLAYER_1_VEST, MAC_ADDRESSES[PLAYER_1_VEST], False)
    #beetle2 = BlunoDevice(PLAYER_1_MPU, MAC_ADDRESSES[PLAYER_1_MPU], True)
    
    #Player-2
    #beetle3 = BlunoDevice(PLAYER_2_GUN, MAC_ADDRESSES[PLAYER_2_GUN], True)
    #beetle4 = BlunoDevice(PLAYER_2_VEST, MAC_ADDRESSES[PLAYER_2_VEST], False)
    #beetle5 = BlunoDevice(PLAYER_2_MPU, MAC_ADDRESSES[PLAYER_2_MPU], True)
    
    #Testers
    beetle6 = BlunoDevice(TEST_GUN, MAC_ADDRESSES[TEST_GUN], True)
    beetle7 = BlunoDevice(TEST_VEST, MAC_ADDRESSES[TEST_VEST], False)
    beetle8 = BlunoDevice(TEST_MPU, MAC_ADDRESSES[TEST_MPU], True)
    
    logging.info('Instantiation of threads')
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(beetle6.reys_transmission_protocol, ('beetle-6'))
        #executor.submit(beetle7.reys_transmission_protocol, ('beetle-7'))
        #executor.submit(beetle8.reys_transmission_protocol, ('beetle-8'))
