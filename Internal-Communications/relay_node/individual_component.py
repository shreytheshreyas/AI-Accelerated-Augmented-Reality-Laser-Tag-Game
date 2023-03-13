import csv
import json
import logging
import struct
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from os import system
from queue import Queue

from bluepy.btle import (
    ADDR_TYPE_RANDOM,
    BTLEDisconnectError,
    DefaultDelegate,
    Peripheral,
)
from client import LaptopClient

# Respond Message Buffer size
NUM_OF_BEETLES = 9  # Need to update to 6 to accomodate two players
DATA_BUFFER_SIZE = 20

# BLUNO ID's for the respective players
PLAYER_1_GUN = 0
PLAYER_1_VEST = 1
PLAYER_1_IMU = 2
PLAYER_2_GUN = 3
PLAYER_2_VEST = 4
PLAYER_2_IMU = 5
TEST_GUN = 6
TEST_VEST = 7
TEST_IMU = 8

# Constants for packet types
SYNC = "S"  # Packet type for handshake.
RST = "R"  # For reseting beetle state
ACK = "A"  # Packet type for SYN-acknowledgment.
DATA_ACK = "D"  # Packet type for data-acknowledgment
DATA_NACK = "N"  # Packet type for data-nagative-acknowledgment
IMU = "I"  # The ASCII code associated with I is 73
GUN = "G"  # The ASCII code associated with G is 71
VEST = "V"  # The ASCII code associated with V is 86

PLAYER_JSON_DATA = [
    '{"player": "p1", "sensor": "gun"}',
    '{"player": "p1", "sensor": "vest"}',
    '{"player": "p1", "sensor": "glove"}',
    '{"player": "p2", "sensor": "gun"}',
    '{"player": "p2", "sensor": "vest"}',
    '{"player": "p2", "sensor": "glove"}',
    '{"player": "p1", "sensor": "gun"}',
    '{"player": "p2", "sensor": "vest"}',
    '{"player": "p2", "sensor": "glove"}',
]

MAC_ADDRESSES = {
        0: '',
        1: 'D0:39:72:BF:C3:8F',
        2: 'D0:39:72:BF:CA:D4',
        3: 'D0:39:72:BF:CD:20',
        4: 'D0:39:72:BF:CD:0A',
        5: 'D0:39:72:BF:C8:D8',
        6: 'D0:39:72:BF:C8:89',
        7: 'D0:39:72:BF:C8:D7',
        8: '6C:79:B8:D3:6A:A3'
}


class StatisticsManager:
    beetlesKbps = [0] * NUM_OF_BEETLES
    totalNumOfBytesReceived = [0] * NUM_OF_BEETLES
    beetlesStartTime = [0] * NUM_OF_BEETLES
    dataReceived = [None] * NUM_OF_BEETLES
    fragmentedPacketCounter = [0] * NUM_OF_BEETLES

    dataRateLock = threading.Lock()
    totalNumOfBytesReceivedLock = threading.Lock()
    dataReceivedLock = threading.Lock()
    fragmentedPacketCounterLock = threading.Lock()

    @classmethod
    def set_start_time(cls, beetleId):
        cls.beetlesStartTime[beetleId] = datetime.now()

    @classmethod
    def clear_data_rate(cls, beetleId):
        cls.totalNumOfBytesReceived[beetleId] = 0
        cls.beetlesKbps[beetleId] = 0

    @classmethod
    def calculate_data_rate(cls, beetleId):
        try:
            # cls.totalNumOfBytesReceivedLock.acquire()
            cls.totalNumOfBytesReceived[beetleId] += 20
            # cls.totalNumOfBytesReceivedLock.release()

            resultantDataRate = (cls.totalNumOfBytesReceived[beetleId] * 8) / (
                1000 * (datetime.now() - cls.beetlesStartTime[beetleId]).total_seconds()
            )
            # cls.dataRateLock.acquire()
            cls.beetlesKbps[beetleId] = resultantDataRate
            # cls.dataRateLock.release()
        except Exception as e:
            pass

    @classmethod
    def increment_num_fragmented_packets(cls, beetleId):
        # cls.fragementedPacketCounterLock.acquire()
        cls.fragmentedPacketCounter[beetleId] += 1
        # cls.fragmentedPacketCounterLock.release()

    @classmethod
    def set_beetle_statistics(cls, beetleId, data):
        # cls.dataReceivedLock.acquire()
        cls.dataReceived[beetleId] = data
        # cls.dataReceived.release()
        cls.calculate_data_rate(beetleId)

    @classmethod
    def display_statistics(cls):
        connectionStatus = {True: "Connected", False: "Disconnected"}
        handshakeStatus = {True: "Completed", False: "Not-Completed"}

        system("clear")
        print("\r")

        if cls.dataReceived[TEST_GUN] is not None:
            print(
                f"GUN-DATA #######################################################################################################################################################################"
            )
            print(f"Beetle-Id = {TEST_GUN}")
            print(
                f"Connection-Status = {connectionStatus[StatusManager.get_connection_status(TEST_GUN)]}"
            )
            print(
                f"Handshake-Status = {handshakeStatus[StatusManager.get_connection_status(TEST_GUN)]}"
            )
            print(f"Data Rate of Beetle in Kbps = {cls.beetlesKbps[TEST_GUN]}")
            print(f'sequenceNumber = {cls.dataReceived[TEST_GUN]["sequenceNumber"]}')
            print(
                f'Value received from GUN = {cls.dataReceived[TEST_GUN]["dataValue"]}'
            )
            print(
                f"Total Number of Fragmented Packets = {cls.fragmentedPacketCounter[TEST_GUN]}\n"
            )
        else:
            print("################ NO-GUN-DATA-AVAILABLE ######################\n")

        if cls.dataReceived[TEST_VEST] is not None:
            print(
                f"VEST-DATA #######################################################################################################################################################################"
            )
            print(f"Beetle-Id = {TEST_VEST}")
            print(
                f"Connection-Status = {connectionStatus[StatusManager.get_connection_status(TEST_VEST)]}"
            )
            print(
                f"Handshake-Status = {handshakeStatus[StatusManager.get_connection_status(TEST_VEST)]}"
            )
            print(f"Data Rate of Beetle in Kbps = {cls.beetlesKbps[TEST_VEST]}")
            print(f'sequenceNumber = {cls.dataReceived[TEST_VEST]["sequenceNumber"]}')
            print(
                f'Value received from GUN = {cls.dataReceived[TEST_VEST]["dataValue"]}'
            )
            print(
                f"Total Number of Fragmented Packets = {cls.fragmentedPacketCounter[TEST_VEST]}\n"
            )
        else:
            print("################ NO-VEST-DATA-AVAILABLE ######################\n")

        if cls.dataReceived[PLAYER_2_IMU] is not None:
            print(
                f"IMU-DATA #########################################################################################################################################################################"
            )
            print(f"Beetle-Id = {PLAYER_2_IMU}")
            print(
                f"Connection-Status = {connectionStatus[StatusManager.get_connection_status(PLAYER_2_IMU)]}"
            )
            print(
                f"Handshake-Status = {handshakeStatus[StatusManager.get_connection_status(PLAYER_2_IMU)]}"
            )
            print(f"Data Rate of Beetle in Kbps = {cls.beetlesKbps[PLAYER_2_IMU]}")
            print(
                f'sequenceNumber = {cls.dataReceived[PLAYER_2_IMU]["sequenceNumber"]}'
            )
            print(
                f'Linear-Acceleration-X = {cls.dataReceived[PLAYER_2_IMU]["dataValue"]["imuDataLinearAccelX"]}'
            )
            print(
                f'Linear-Acceleration-Y = {cls.dataReceived[PLAYER_2_IMU]["dataValue"]["imuDataLinearAccelY"]}'
            )
            print(
                f'Linear-Acceleration-Z = {cls.dataReceived[PLAYER_2_IMU]["dataValue"]["imuDataLinearAccelZ"]}'
            )
            print(
                f'Gyro-Acceleration-Y = {cls.dataReceived[PLAYER_2_IMU]["dataValue"]["imuDataGyroAccelX"]}'
            )
            print(
                f'Gyro-Acceleration-Z = {cls.dataReceived[PLAYER_2_IMU]["dataValue"]["imuDataGyroAccelY"]}'
            )
            print(
                f'Gyro-Acceleration-Z = {cls.dataReceived[PLAYER_2_IMU]["dataValue"]["imuDataGyroAccelZ"]}'
            )
            print(
                f'Roll = {cls.dataReceived[PLAYER_2_IMU]["dataValue"]["imuDataRoll"]}'
            )
            print(
                f'Pitch = {cls.dataReceived[PLAYER_2_IMU]["dataValue"]["imuDataPitch"]}'
            )
            print(f'Yaw = {cls.dataReceived[PLAYER_2_IMU]["dataValue"]["imuDataYaw"]}')
            print(
                f"Total Number of Fragmented Packets = {cls.fragmentedPacketCounter[PLAYER_2_IMU]}\n"
            )
        else:
            print("################ NO-IMU-DATA-AVAILABLE ######################\n")


"""
BufferManager DOCUMENTATION
"""


class BufferManager:
    relayNodeBuffer = Queue(DATA_BUFFER_SIZE)

    @classmethod
    def insertDataValue(cls, beetle_id, dataValue):
        relayNodeBuffer.put(dataValue)

    @classmethod
    def transferDataValue(cls):
        pass


"""
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
    
    - Following are the locks associated with thislist object:
        * dataNackStatusLock 

"""


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

    @classmethod
    def set_status(cls, name, lock, flags, beetle_id, value):
        lock.acquire()
        # print(f'Acquire {name} status {beetle_id}')
        flags[beetle_id] = value
        lock.release()
        # print(f'Release {name} status {beetle_id}')

    # METHODS ASSOCIATED WITH CONNECTION BUFFER
    @classmethod
    def set_connection_status(cls, beetle_id):
        cls.set_status(
            "conn", cls.connectionStatusLock, cls.connectionStatusFlags, beetle_id, True
        )

    @classmethod
    def clear_connection_status(cls, beetle_id):
        cls.set_status(
            "conn",
            cls.connectionStatusLock,
            cls.connectionStatusFlags,
            beetle_id,
            False,
        )

    @classmethod
    def get_connection_status(cls, beetle_id):
        return cls.connectionStatusFlags[beetle_id]

    # METHODS ASSOCIATED WITH RESET BUFFER
    @classmethod
    def set_reset_status(cls, beetle_id):
        cls.set_status(
            "reset", cls.resetStatusLock, cls.resetStatusFlags, beetle_id, True
        )

    @classmethod
    def clear_reset_status(cls, beetle_id):
        cls.set_status(
            "reset", cls.resetStatusLock, cls.resetStatusFlags, beetle_id, False
        )

    @classmethod
    def get_reset_status(cls, beetle_id):
        return cls.resetStatusFlags[beetle_id]

    # METHODS ASSOCIATED WITH SYNC BUFFER
    @classmethod
    def set_sync_status(cls, beetle_id):
        cls.set_status("sync", cls.syncStatusLock, cls.syncStatusFlags, beetle_id, True)

    @classmethod
    def clear_sync_status(cls, beetle_id):
        cls.set_status(
            "sync", cls.syncStatusLock, cls.syncStatusFlags, beetle_id, False
        )

    @classmethod
    def get_sync_status(cls, beetle_id):
        return cls.syncStatusFlags[beetle_id]

    # METHODS ASSOCIATED WITH ACK BUFFER
    @classmethod
    def set_ack_status(cls, beetle_id):
        cls.set_status("ack", cls.ackStatusLock, cls.ackStatusFlags, beetle_id, True)

    @classmethod
    def clear_ack_status(cls, beetle_id):
        cls.set_status("ack", cls.ackStatusLock, cls.ackStatusFlags, beetle_id, False)

    @classmethod
    def get_ack_status(cls, beetle_id):
        return cls.ackStatusFlags[beetle_id]

    # METHODS ASSOCIATED WITH DATA-ACK BUFFER
    @classmethod
    def set_data_ack_status(cls, beetle_id):
        cls.set_status(
            "data ack", cls.dataAckStatusLock, cls.dataAckStatusFlags, beetle_id, True
        )

    @classmethod
    def clear_data_ack_status(cls, beetle_id):
        cls.set_status(
            "data ack", cls.dataAckStatusLock, cls.dataAckStatusFlags, beetle_id, False
        )

    @classmethod
    def get_data_ack_status(cls, beetle_id):
        return cls.dataAckStatusFlags[beetle_id]

    # METHODS ASSOCIATED WITH DATA-NACK BUFFER
    @classmethod
    def set_data_nack_status(cls, beetle_id):
        cls.set_status(
            "data nack",
            cls.dataNackStatusLock,
            cls.dataNackStatusFlags,
            beetle_id,
            True,
        )

    @classmethod
    def clear_data_nack_status(cls, beetle_id):
        cls.set_status(
            "data nack",
            cls.dataNackStatusLock,
            cls.dataNackStatusFlags,
            beetle_id,
            False,
        )

    @classmethod
    def get_data_nack_status(cls, beetle_id):
        return cls.dataNackStatusFlags[beetle_id]


class BluetoothInterfaceHandler(DefaultDelegate):
    def __init__(self, beetleId, laptopClient):
        DefaultDelegate.__init__(self)
        self.beetleId = beetleId
        self.receivingBuffer = b""
        self.imuDataFeatureVectors = defaultdict(dict)
        self.imuDataFlagCounter = 0
        self.imuDataFlags = {
            "linear-accel-vector": False,
            "gyro-accel-vector": False,
            "rotational-force-vector": False,
        }
        self.laptopClient = laptopClient

    def verify_checksum(self, packetData):
        checksum = 0
        for idx in range(len(packetData) - 1):
            checksum = checksum ^ packetData[idx]
        return packetData[19] == checksum

    def handleNotification(self, cHandle, data):
        # system('clear')
        # print('\r')

        try:
            self.receivingBuffer += data
            if len(self.receivingBuffer) == 1:
                if self.receivingBuffer.decode("ascii") == RST:
                    StatusManager.set_reset_status(self.beetleId)

                if self.receivingBuffer.decode("ascii") == ACK:
                    StatusManager.set_sync_status(self.beetleId)

                self.receivingBuffer = b""

            elif len(self.receivingBuffer) >= 20:
                packetData = self.receivingBuffer[0:20]
                self.receivingBuffer = self.receivingBuffer[20:]
                data = {}
                isPacketCorrect = self.verify_checksum(packetData)

                if isPacketCorrect:
                    packetType = struct.unpack("b", packetData[1:2])[0]
                    if chr(packetType) == GUN:
                        gunData = struct.unpack("B", packetData[2:3])[0]

                        if gunData == 1:
                            print("Ammo decreased by one count")

                        if gunData == 13:
                            print("Gun is out of ammo")

                        StatisticsManager.set_beetle_statistics(self.beetleId, data)

                    if chr(packetType) == VEST:
                        vestData = struct.unpack("B", packetData[2:3])[0]
                        print(f"vest data received = {vestData}")
                        if vestData == 1:
                            print("Player health decreased by 10HP")

                        if vestData == 13:
                            print("Player is dead")

                        StatisticsManager.set_beetle_statistics(self.beetleId, data)

                    if chr(packetType) == IMU:
                        imuDataFeatureVector = {}
                        imuDataFeatureVector["timestamp"] = (datetime.now()).timestamp()
                        imuDataFeatureVector["imuDataLinearAccelX"] = (
                            struct.unpack(">h", packetData[2:4])[0] / 1024
                        )
                        imuDataFeatureVector["imuDataLinearAccelY"] = (
                            struct.unpack(">h", packetData[4:6])[0] / 1024
                        )
                        imuDataFeatureVector["imuDataLinearAccelZ"] = (
                            struct.unpack(">h", packetData[6:8])[0] / 1024
                        )
                        imuDataFeatureVector["imuDataGyroAccelX"] = (
                            struct.unpack(">h", packetData[8:10])[0] / 128
                        )
                        imuDataFeatureVector["imuDataGyroAccelY"] = (
                            struct.unpack(">h", packetData[10:12])[0] / 128
                        )
                        imuDataFeatureVector["imuDataGyroAccelZ"] = (
                            struct.unpack(">h", packetData[12:14])[0] / 128
                        )
                        # imuDataFeatureVector['label'] = 'grenade'
                        imuDataFeatureVector["label"] = "shield"
                        # imuDataFeatureVector['label'] = 'reload'
                        # print(packetData)
                        print(imuDataFeatureVector)
                    StatusManager.set_data_ack_status(self.beetleId)

                # else:
                #     logging.info("Packet is corrupted!")
                #     StatusManager.set_data_nack_status(self.beetleId)

            else:
                # if data is not coming out to be correct comment out these two lines
                # self.receivingBuffer = b''
                print("Packet is fragmented")
                StatisticsManager.increment_num_of_fragmented_packets(self.beetleId)
                pass
        except Exception as e:
            logging.info(
                f"handleNotfications: Something Went wrong. please see the exception message below:\n {e}"
            )
            print(self.imuDataFeatureVectors)


class BlunoDevice:
    def __init__(self, beetleId, macAddress):
        self.beetleId = beetleId
        self.macAddress = macAddress
        self.peripheral = None
        self.blutoothInterfaceHandler = None
        self.laptopClient = LaptopClient("192.168.95.250", 8080)
        self.connectedToUltra = False

    def transmit_packet(self, data):
        try:
            for characteristic in self.peripheral.getCharacteristics():
                characteristic.write(bytes(data, "ascii"), withResponse=False)
        except (BTLEDisconnectError, AttributeError):
            pass
        except Exception as e:
            logging.info(
                f"Some thing went wrong while trying to transmit packet to {self.beetleId}, please refer to the following exception:\n {e}"
            )

    def connect_to_ultra96(self):
        self.laptopClient.connect()
        self.laptopClient.send_plaintext(PLAYER_JSON_DATA[self.beetleId])
        receivedMessage = self.laptopClient.recv_msg()
        logging.info(
            f"Connection successfully established between relay node and ultra-96 - {receivedMessage}"
        )
        self.connectedToUltra = True

    def close_connection_to_ultra96(self):
        self.laptopClient.close()
        logging.info(f"Closed connection between relay node and ultra-96")
        self.connectedToUltra = False

    def establish_connection(self):
        try:
            self.peripheral = Peripheral(self.macAddress)
            self.bluetoothInterfaceHandler = BluetoothInterfaceHandler(
                self.beetleId, self.laptopClient
            )
            self.peripheral.withDelegate(self.bluetoothInterfaceHandler)
            StatusManager.set_connection_status(self.beetleId)
            logging.info(
                f"Connection successfully established between the beetle-{self.beetleId} and relay node."
            )

        except Exception as e:
            logging.info(
                f"Could not connect to bluno device: {self.beetleId} due to the following exception.\n {e}"
            )

    def reset_controller(self):
        try:
            self.transmit_packet(RST)
            self.peripheral.waitForNotifications(1.0)
        except (BTLEDisconnectError, AttributeError):
            pass
        except Exception as e:
            logging.info(
                f"Some thing went wrong while trying to reset {self.beetleId}, please refer to the following exception:\n {e}"
            )

    def handshake_mechanism(self, isHandshakeCompleted):
        print("Start of handshake protocol")
        if StatusManager.get_connection_status(self.beetleId):
            self.transmit_packet(SYNC)
            self.peripheral.waitForNotifications(1.0)

            if StatusManager.get_sync_status(self.beetleId):
                self.transmit_packet(ACK)
                StatusManager.set_ack_status(self.beetleId)
                isHandshakeCompleted = True
                logging.info(f"Handshake Completed for beetle-{self.beetleId}\n")

        print("End of handshake protocol", isHandshakeCompleted)
        return isHandshakeCompleted

    def transmission_protocol(self):
        isHandshakeCompleted = False
        while True:
            try:
                if not isHandshakeCompleted:
                    if not StatusManager.get_connection_status(self.beetleId):
                        print("Establishing connection")
                        self.establish_connection()
                    if not StatusManager.get_reset_status(self.beetleId):
                        self.reset_controller()
                        StatisticsManager.clear_data_rate(self.beetleId)
                        StatisticsManager.set_start_time(self.beetleId)

                    isHandshakeCompleted = self.handshake_mechanism(
                        isHandshakeCompleted
                    )

                    if isHandshakeCompleted:
                        self.connect_to_ultra96()
                else:
                    # regular data transfer
                    # StatisticsManager.display_statistics()
                    self.peripheral.waitForNotifications(0.1)

                    if StatusManager.get_data_ack_status(self.beetleId):
                        # self.laptopClient.send_plaintext(BufferManager.relayNodeBuffer.get())
                        self.transmit_packet(DATA_ACK)
                        StatusManager.clear_data_ack_status(self.beetleId)

                    if StatusManager.get_data_nack_status(self.beetleId):
                        self.transmit_packet(DATA_NACK)
                        StatusManager.clear_data_nack_status(self.beetleId)

            except KeyboardInterrupt:
                logging("Program terminated due a keyboard interrupt")
                self.peripheral.disconnect()

            # except Exception as e:
            # logging.info(f'something went wrong due to the following error: \n {e}')

            except (BTLEDisconnectError, AttributeError):
                logging.info(
                    f"Beetle-{self.beetleId} been disconnected due to a significantly large distance from the relay node"
                )
                logging.info(f"Attempting Reconnection")
                isHandshakeCompleted = False
                StatusManager.clear_connection_status(self.beetleId)
                StatusManager.clear_reset_status(self.beetleId)
                StatusManager.clear_sync_status(self.beetleId)
                StatusManager.clear_ack_status(self.beetleId)
                StatusManager.clear_data_ack_status(self.beetleId)
                StatusManager.clear_data_nack_status(self.beetleId)

                if self.connectedToUltra:
                    self.close_connection_to_ultra96()
                pass


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    # Player-1
    beetle0 = BlunoDevice(PLAYER_1_GUN, MAC_ADDRESSES[PLAYER_1_GUN])
    beetle1 = BlunoDevice(PLAYER_1_VEST, MAC_ADDRESSES[PLAYER_1_VEST])
    beetle2 = BlunoDevice(PLAYER_1_IMU, MAC_ADDRESSES[PLAYER_1_IMU])

    # Player-2
    beetle3 = BlunoDevice(PLAYER_2_GUN, MAC_ADDRESSES[PLAYER_2_GUN])
    beetle4 = BlunoDevice(PLAYER_2_VEST, MAC_ADDRESSES[PLAYER_2_VEST])
    beetle5 = BlunoDevice(PLAYER_2_IMU, MAC_ADDRESSES[PLAYER_2_IMU])

    # Testers
    beetle6 = BlunoDevice(TEST_GUN, MAC_ADDRESSES[TEST_GUN])
    beetle7 = BlunoDevice(TEST_VEST, MAC_ADDRESSES[TEST_VEST])
    beetle8 = BlunoDevice(TEST_IMU, MAC_ADDRESSES[TEST_IMU])

    # Instantiation of Threads
    logging.info("Instantiation of threads")
    # beetleThread0 = threading.Thread(target=beetle0.transmission_protocol, args=())
    beetleThread1 = threading.Thread(target=beetle1.transmission_protocol, args=())
    beetleThread2 = threading.Thread(target=beetle2.transmission_protocol, args=())
    beetleThread3 = threading.Thread(target=beetle3.transmission_protocol, args=())
    beetleThread4 = threading.Thread(target=beetle4.transmission_protocol, args=())
    beetleThread5 = threading.Thread(target=beetle5.transmission_protocol, args=())
    beetleThread6 = threading.Thread(target=beetle6.transmission_protocol, args=())
    beetleThread7 = threading.Thread(target=beetle7.transmission_protocol, args=())
    beetleThread8 = threading.Thread(target=beetle8.transmission_protocol, args=())

    # Starting beetle Threads
    # beetleThread0.start()
    # beetleThread1.start()
    # beetleThread2.start()
    beetleThread3.start()
    # beetleThread4.start()
    # beetleThread5.start()
    # beetleThread6.start()
    # beetleThread7.start()
    # beetleThread8.start()

    # Terminating beetle Threads
    # beetleThread0.join()
    # beetleThread1.join()
    # beetleThread2.join()
    beetleThread3.join()
    # beetleThread4.join()
    # beetleThread5.join()
    # beetleThread6.join()
    # beetleThread7.join()
    # beetleThread8.join()
