from bluepy.btle import Peripheral, DefaultDelegate, BTLEDisconnectError
from concurrent.futures import ThreadPoolExecutor
from Queue import queue
import threading 
import logging
import time 

#Respond Message Buffer size
RESPONSE_BUFFER_SIZE = 3
COMMON_DATA_BUFFER_SIZE = 20

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

MAC_ADDRESSES = {
        0: "D0:39:72:BF:CA:D4",
        1: "D0:39:72:BF:C3:8F",
        2: "D0:39:72:BF:C8:D8"
}

class BufferManager:
    synchronizationBuffer = [False] * RESPONSE_BUFFER_SIZE
    acknowledgementBuffer = [False] * RESPONSE_BUFFER_SIZE
    negativeAcknowledgementBuffer = [False] * RESPONSE_BUFFER_SIZE
    commonDataBuffer = queue(COMMON_DATA_BUFFER_SIZE)

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

class BlunoDelegate(DefaultDelegate):
    pass

class BlunoDevice:
    def __init__(self, beetle_id, mac_address, isARQ):
        self.beetle_id = beetle_id
        self.mac_address = mac_address
        self.isARQ = isARQ ### No need to keep track of nagative-acknowledgement-buffer if this is set to false 
        #self.connection_interface = Peripheral()

    def connect(self, text):
        logging.info(f'In connect method {text}')
        while True:
            try: 
                Peripheral(self.mac_address)
                print('connection successful')
                break
            except Exception as e:
                print(f'Could not connect to bluno device: {text}')
                break
    
    def transmit_data(self, data):
        pass
    
    def handshake_mechanism(self, isHandshakeCompleted):
        
        ##Acuring buffer lock for each repestive thread so th
        while not isHandshakeCompleted:
            if not BufferManager.get_sync_status(self.beetle_id):
                self.transmit_data(SYN)
                ### Assuming transmission medium and 100% reliable and no possibilty of packet loss
                BufferManager.flip_sycn_status(self.beetle_id)
            
            elif BufferManager.get_ack_status(self.beetle_id):
                BufferManager.flip_ack_status(self.beetle_id)
                BufferManager.flip_sync_status(self.beetle_id)
                isHandshakeCompleted = True 
            
            else:
                continue

        return isHandshakeCompleted
    
    def transmission_protocol():
        isHandshakeCompleted = False
        while True: 
            if not isHandshakeCompleted:
                #1. Connect/Reconnect to bettle 
                self.connect(self.beetle_id)
                #2. Send Synchronization packet
                isHandshakeCompleted = self.handshake_mechanism(isHandshakeCompleted)
                #3. Wait for ACK from bluno
                #4. If ACK is received from bluno, send an ACK from your end as well 
                            
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
        executor.submit(beetle1.connect, ('beetle-1'))
        executor.submit(beetle2.connect, ('beetle-2'))
        executor.submit(beetle3.connect, ('beetle-3'))
