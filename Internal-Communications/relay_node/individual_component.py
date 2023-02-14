from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError, AssignedNumbers
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading 
import logging
import time 



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
FIN = 'F' #Packet type for closing connection.
ACK = 'A' #Packet type for acknowledgment. 
IMD = 'I' #Packet type for IMU data.
GAM = 'B' #Packet type for Gun-Ammo. Identified by B which means bullet.
GSH = 'H' #Packet type for Gun-Shot. Identified by H which means hit.

#Services and Characteristics for the GATT layer of the protocol stack which is important for data communication between 
#the central device and the respective peripherals, i.e the beetles.
#GATT_SERVICE_UUID = "0000dfb0-0000-1000-8000-00805f9b34fb"
#GATT_WRITE_CHARACTERISTIC_UUID = "0000dfb1-0000-1000-8000-00805f9b34fb"

GATT_SERVICE_UUID = "DFBO"
GATT_WRITE_CHARACTERISTIC_UUID = "DFB1"


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

class BufferManager:
    synchronizationBuffer = [False] * RESPONSE_BUFFER_SIZE #Used for synchronization 
    acknowledgementBuffer = [False] * RESPONSE_BUFFER_SIZE #Used for data transfer
    negativeAcknowledgementBuffer = [False] * RESPONSE_BUFFER_SIZE #Used for Data transfer
    commonDataBuffer = Queue(DATA_BUFFER_SIZE)
    
    @classmethod
    def flip_sync_status(cls, beetle_id):
       cls.synchronizationBuffer[beetle_id] = not cls.synchronizationBuffer[beetle_id]
    
    @classmethod
    def flip_ack_status(cls, beetle_id):
       cls.acknowledgementBuffer[beetle_id] = not cls.acknowledgementBuffer[beetle_id]
    
    @classmethod
    def flip_nack_status(cls, beetle_id):
       cls.negativeAcknowledgementBuffer[beetle_id] = not cls.negativeAcknowledgementBuffer[beetle_id]
    
    @classmethod
    def set_data_buffer(cls, beetle_id, data):
        logging.info(f'common-data-buffer being set by beetle-{beetle_id}')
        dataBufferLock.acquire()
        ####initialize commonDataBuffer with incomming data####
        dataBufferLock.release()
        pass
    
    @classmethod
    def get_sync_status(cls, beetle_id):
        return cls.synchronizationBuffer[beetle_id]
    
    @classmethod
    def get_ack_status(cls, beetle_id):
        return cls.acknowledgementBuffer[beetle_id]
    
    @classmethod
    def get_nack_status(cls, beetle_id):
        return cls.negativeAcknowledgementBuffer[beetle_id]
    
    @classmethod
    def get_data_buffer(cls):
        return cls.commonDataBuffer



class BluetoothInterfaceHandler(DefaultDelegate):
    def __init__(self, beetleId):
        DefaultDelegate.__init__(self)
        self.beetleId = beetleId
        self.receivingBuffer = b'' 
    
    def handleNotification(self, cHandle, data):
        self.receivingBuffer += data
        print(self.receivingBuffer)
        logging.info(f'inside handle norifications function of beetle: {self.beetleId}')
        if len(self.receivingBuffer) == 1 and self.receivingBuffer.decode(encoding='ascii') == 'A':
            #Steps to deal with acknowledgement sent from the arduino 
            print(f'The Transmitted information is as follows:\n')
            print(len(self.receivingBuffer) == 1)
            print(self.receivingBuffer.decode(encoding='ascii'))
            print(self.receivingBuffer)
            logging.info(f'ACK received from beetle-{self.beetleId} successfully')
            #Flip flag bit associated with the beetleId to the set state so as to 
            #indicate that the synchronize packet has been acknowledged.
            BufferManager.flip_sync_status(self.beetleId)

        elif len(self.receivingBuffer) <= 20:
            print(f'Data received from {self.beetleId} successfully. The data is as follows: \n')
            print(self.receivingBuffer.decode(encoding='ascii'))
            print(self.recevingBuffer)
        else: #Dealing with the case where data spans across multiple packets
            print('Packet is fragmented')




class BlunoDevice:
    def __init__(self, beetleId, macAddress, isARQ):
        self.beetleId = beetleId
        self.macAddress = macAddress
        self.peripheral = None
        self.blutoothInterfaceHandler = None 
        self.isARQ = isARQ ### No need to keep track of nagative-acknowledgement-buffer if this is set to false 

    def establish_connection(self, text):
        logging.info(f'In connect method {text}')
        while True:
            try: 
                self.peripheral = Peripheral(self.macAddress)
                #Peripheral(self.macAddress) 
                self.bluetoothInterfaceHandler = BluetoothInterfaceHandler(self.beetleId)
                self.peripheral.withDelegate(self.bluetoothInterfaceHandler)
                #logging.info(self.peripheral.getCharacteristics())
                logging.info(f'Connection successfully established between the beetle-{self.beetleId} and relay node.')
                #self.peripheral.waitForNotifications(1)
                logging.info('finished waiting for notifications')
                break
            except Exception as e:
                logging.info(f'Could not connect to bluno device: {self.beetleId} due to the following exception.\n {e}')
                break
    
    def transmit_data(self, data):
        try:
            logging.info('before intialization of transmit_data function')
            #serialService = self.peripheral.getServiceByUUID(GATT_SERVICE_UUID)
            #serialServiceChararacteristics = serialService.getCharacteristics(GATT_SERVICE_UUID)
            
            logging.info('before for loop of transmit_data function')
            for characteristic in self.peripheral.getCharacteristics():
                logging.info('Inside for loop of transmit_data function')
                #if characteristic == GATT_WRITE_CHARACTERISTIC_UUID: 
                characteristic.write(bytes(data,'ascii'), withResponse=False)
                logging.info(f'data transmitted over to beetle {self.beetleId}')

        except Exception as e:
            logging.info(f'Something went wrong during the transmission process: \n {e}')

    def handshake_mechanism(self, isHandshakeCompleted):
        while not isHandshakeCompleted:
            logging.info(f'Still in handshaking mechanism for beetle-{self.beetleId}')
            if not BufferManager.get_sync_status(self.beetleId):
                #Step-1: Transmit synchronization packet from relay node 
                self.transmit_data(SYN)
                #Step-2: Wait for ACK from peripheral to make sure it received the SYN packet
                self.peripheral.waitForNotifications(1.0) 
                logging.info('synchronization flag set in handshake mechanism')
                self.transmit_data(ACK)
            else:    
                #Step-3: Flip synchronization flag for the associated beetle to a intital state
                BufferManager.flip_sync_status(self.beetleId)
                #Step-4: set handshake 
                isHandshakeCompleted = True 
        
        logging.info(f'Handshake established with beetle-{self.beetleId}')
        logging.info('synchronization flag associated with beetle-{self.beetleId} is cleared')
        return isHandshakeCompleted
    
    def reys_transmission_protocol(self,text):
        isHandshakeCompleted = False
        try:
            while True: 
                if not isHandshakeCompleted:
                    #1. Connect/Reconnect to bettle 
                    self.establish_connection(self.beetleId)
                    #2. perform handshake mechanism 
                    isHandshakeCompleted = self.handshake_mechanism(isHandshakeCompleted)
                    #3. Wait for ACK from bluno
                    #4. If ACK is received from bluno, send an ACK from your end as well 
                else:
                    #regular data transfer
                    self.transmit_data('D')
                    logging.info(f'Code involed for data communication between relay node and beetle {self.beetleId} \r')
                    self.peripheral.waitForNotifications(0.1)
                    
        except KeyboardInterrupt:
            self.peripheral.disconnect()
            print(f'Beetle-{self.beetleId} been disconnected due to a keyboard interrupt on the relay node')
        
        except BTLEDisconnectError:
            print(f'Beetle-{self.beetleId} been disconnected due to a significantly large distance from the relay node')
            isHandshakeCompleted = False
            pass

        except Exception as e:
            print(f'Something went wrong in protocol with beetle{self.beetleId}')
            print(f'Refer to the following exception below:\n {e}')

    def dummy(self, text):
        print(f'This message is from {text}')

if __name__ == '__main__':
    
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")  
    #Instantiating six threads 
    #Three threads are allocated to one player 
    #Each of the three threads correspond to the respective blunos connected to the IR blaster, IR reciever and The IMU
    
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
    
    logging.info('Before Instantiation of threads')
    with ThreadPoolExecutor(max_workers=3) as executor:
        #executor.submit(beetle6.reys_transmission_protocol, ('beetle-6'))
        executor.submit(beetle7.reys_transmission_protocol, ('beetle-7'))
        #executor.submit(beetle8.reys_transmission_protocol, ('beetle-8'))
