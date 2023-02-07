from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading 
import logging
import time 



#Respond Message Buffer size
RESPONSE_BUFFER_SIZE = 3 #Need to update to 6 to accomodate two players
DATA_BUFFER_SIZE = 20

#BLUNO ID's for the respective players 
PLAYER_1_GUN = 0
PLAYER_1_VEST = 1
PLAYER_1_MPU = 2
PLAYER_2_GUN = 3
PLAYER_2_VEST = 4
PLAYER_2_MPU = 5

#Constants for packet types 
SYN = 'S' #Packet type for handshake. 
FIN = 'F' #Packet type for closing connection.
ACK = 'A' #Packet type for acknowledgment. 
IMD = 'I' #Packet type for IMU data.
GAM = 'B' #Packet type for Gun-Ammo. Identified by B which means bullet.
GSH = 'H' #Packet type for Gun-Shot. Identified by H which means hit.

#Services and Characteristics for the GATT layer of the protocol stack which is important for data communication between 
#the central device and the respective peripherals, i.e the beetles.
GATT_SERVICE_UUID = "0000dfb0-0000-1000-8000-00805f9b34fb"
GATT_WRITE_CHARACTERISTIC_UUID = "0000dfb1-0000-1000-8000-00805f9b34fb"

MAC_ADDRESSES = {
        0: "D0:39:72:BF:CA:D4",
        1: "D0:39:72:BF:C3:8F",
        2: "D0:39:72:BF:C8:D8"
}

class BufferManager:
    synchronizationBuffer = [False] * RESPONSE_BUFFER_SIZE #Used for synchronization 
    acknowledgementBuffer = [False] * RESPONSE_BUFFER_SIZE #Used for data transfer
    negativeAcknowledgementBuffer = [False] * RESPONSE_BUFFER_SIZE #Used for Data transfer
    commonDataBuffer = Queue(DATA_BUFFER_SIZE)

    def flip_sync_status(cls, bettle_id):
       synchronizationBuffer[beetle_id] = not synchronizationBuffer[beetle_id]

    def flip_ack_status(cls, bettle_id):
       acknowledgementBuffer[beetle_id] = not acknowledgementBuffer[beetle_id]

    def flip_nack_status(cls, bettle_id):
       negativeAcknowledgementBuffer[beetle_id] = not negativeAcknowledgementBuffer[beetle_id]
    
    def set_data_buffer(cls, beetle_id, data):
        logging.info(f'common-data-buffer being set by beetle-{beetle_id}')
        dataBufferLock.acquire()
        ####initialize commonDataBuffer with incomming data####
        dataBufferLock.release()
        pass

    def get_sync_status(cls, bettle_id):
        return synchronizationBuffer[beetle_id]
    
    def get_ack_status(cls, beetle_id):
        return acknowledgementBuffer[beetle_id]
    
    def get_nack_status(cls, beetle_id):
        return negativeAcknowledgementBuffer[beetle_id]
    
    def get_data_buffer(cls):
        return commonDataBuffer



class BluetoothInterfaceHandler(DefaultDelegate):
    def __init__(self, beetleId):
        DefaultDelegate.__init__(self)
        self.beetleId = beetleId
        self.receivingBuffer = b'' 
    
    def handleNotification(self, cHandle, data):
        self.receivingBuffer += data
        
        #Steps to deal with acknowledgement sent from the arduino 
        print(f'The Transmitted information is as follows:\n')
        print(len(self.receivingBuffer) == 1)
        print(self.receivingBuffer.decode(encoding='ascii'))
        print(self.receivingBuffer)

        if len(self.receivingBuffer) == 1 and self.receivingBuffer.decode(encoding='ascii') == 'A':
            logging.info(f'ACK received from beetle-{self.beetleId} successfully')
            BufferManger.flip_sync_status(self.beetleId)

        elif len(self.receivingBuffer) <= 20:
                pass
        else: #Dealing with the case where data spans across multiple packets
            pass




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
                self.peripheral.setDelegate(self.bluetoothInterfaceHandler)
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
            serialService = self.peripheral.getServiceByUUID(GATT_SERVICE_UUID)
            serialServiceChararacteristics = serialService.getCharacteristics(serialService)

            for characteristic in serialServiceCharacteristics:
                if characteristic == GATT_WRITE_CHARACTERISTIC_UUID:
                    characteristic.write(bytes(data, 'ascii'), withResponse=True)
                    logging.info(f'data transmitted over to beetle-{self.beetleId}')

        except Exception as e:
            logging.info(f'Service associated with the given service uuid does not exist. Exception is as follows: \n {e}')
        
    def handshake_mechanism(self, isHandshakeCompleted):
        while not isHandshakeCompleted:
            logging.info(f'Still in handshaking mechanism for beetle-{self.beetleId}')
            if not BufferManager.get_sync_status(self.beetle_id):
                #Step-1: Transmit synchronization packet from relay node 
                self.transmit_data(SYN)
                #Step-2: Wait for ACK from peripheral to make sure it received the SYN packet
                self.peripheral.waitForNotifications(1.0) 
            else:    
                #Step-3: Flip synchronization flag for the associated beetle to a intital state
                BufferManager.flip_sync_status(self.beetle_id)
                #Step-4: set handshake 
                isHandshakeCompleted = True 
        
        logging.info(f'Handshake established with beetle-{self.beetle.Id}')
        return isHandshakeCompleted
    
    def reys_transmission_protocol():
        isHandshakeCompleted = False
        while True: 
            if not isHandshakeCompleted:
                #1. Connect/Reconnect to bettle 
                self.establish_connection(self.beetle_id)
                #2. perform handshake mechanism 
                isHandshakeCompleted = self.handshake_mechanism(isHandshakeCompleted)
                #3. Wait for ACK from bluno
                #4. If ACK is received from bluno, send an ACK from your end as well 
            else:
                pass
                #regular data transfer


    def dummy(self, text):
        print(f'This message is from {text}')

if __name__ == '__main__':
    
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")  
    #Instantiating six threads 
    #Three threads are allocated to one player 
    #Each of the three threads correspond to the respective blunos connected to the IR blaster, IR reciever and The IMU
    
    beetle1 = BlunoDevice(PLAYER_1_GUN, MAC_ADDRESSES[PLAYER_1_GUN], True)
    beetle2 = BlunoDevice(PLAYER_1_VEST, MAC_ADDRESSES[PLAYER_1_VEST], False)
    beetle3 = BlunoDevice(PLAYER_1_MPU, MAC_ADDRESSES[PLAYER_1_MPU], True)
     
    logging.info('Before Instantiation of threads')
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(beetle1.establish_connection, ('beetle-1'))
        #executor.submit(beetle2.establish_connection, ('beetle-2'))
        #executor.submit(beetle3.establish_connection, ('beetle-3'))
