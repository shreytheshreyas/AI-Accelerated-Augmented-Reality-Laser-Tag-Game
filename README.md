# NUS Computer Engineering Capstone Project: Augmented Reality AI Accelerated Laser Tag Game

## Project Overview and System Functionalities

### Overview
This project develops an innovative augmented reality laser tag system designed for multiplayer combat scenarios. The system enables dynamic gameplay between two or more players within a designated arena, maintaining optimal engagement distances of 7-10 meters between participants.
Each player's equipment consists of three integrated wearable components: a tactical gun, a sensor-equipped vest, and a smart glove. The gun incorporates infrared transmitters to create realistic laser-based combat interactions, while the vest features strategic sensor placement to accurately detect incoming shots. The smart glove employs advanced gesture recognition sensors, allowing players to execute various in-game commands and actions through natural hand movements during combat.
These interconnected components work together to create an immersive augmented reality combat experience that blends physical movement with digital gameplay elements.

### Player Actions
Players should be able to carry out the following actions during the game:
Shoot: Target and inflict damage on opponent in line of sight with laser gun.
Reload: Replenish ammo when depleted.
Shield: Gesture-activated protection.
Grenade: Gesture-based throwing action to damage opponent in line of sight.
Logout: Gesture to end game and logout.

### User Stories
| As a | I want to | so that |
|----------------|-----------|----------|
| Player | log into the laser tag game | I can play the laser tag game |
| Player | shoot my opponent in my line of sight within 7-10m | I can damage my opponent |
| Player | play for 60 mins without disconnection | I can have smooth gameplay |
| Player | see game statistics (health, ammo, shield) | I can plan an efficient gameplay stratergy |
| Player | know when I hit my opponent | I can confirm my aim |
| Player | throw a grenade in my line of sight | I can inflict grenade damage |
| Player | activate my shield | I can protect myself from potential attacks|
 
## System Architecture 
The system implements a sophisticated laser tag game utilizing an Ultra96 board as its central processing unit. Multiple hardware components connect to this board to enable gameplay features including motion detection, shot registration, and real-time state management.

### Core Hardware Components

#### Illustration of Overall Architecture
![System Architecture Overview Diagram](./Image_Assets/system_architecture.png)
*Figure 2.1.1: Complete system architecture showing interconnections between hardware components and the Ultra96 board*

#### Wearable Components
##### Sensor Placement in Wearable Components
The system features three primary wearable components that players use during gameplay. The following Diagram showcases the placement of the hardware sensors on the respective components.
![Sensor Placement in Wearable Components](./Image_Assets/sensor_placement.png)
*Figure 2.2.3: The above figure showcases the placement of the sensors we utilized on the players wearables*

1. **Gun Assembly**
   - Equipped with IR transmitters
   - Integrated bullet count display
   - Provides real-time ammunition feedback

![Gun Component Layout](./Image_Assets/gun_layout.png)
*Figure 2.2.3: Detailed gun assembly showing IR transmitter placement and display integration*

2. **Tactical Vest**
   - Features IR receivers for shot detection
   - Includes HP display for health monitoring
   - Strategic sensor placement for optimal detection

![Vest Component Layout](./Image_Assets/vest_layout.png)
*Figure 2.2.2: Vest design showing IR receiver placement and display mounting points*

3. **Smart Glove**
   - Integrated motion sensors
   - Enables gesture detection
   - Provides real-time movement data
![Action Glove Component Layout](./Image_Assets/action_glove_layout.png)

### Ultra96 Process Architecture

The system implements a sophisticated multi-process architecture on the Ultra96 board, utilizing multiprocessing queues and arrays for robust inter-process communication.

#### Process 1: Relay Server
This primary process manages all hardware component communications through several child processes:

1. **Update Beetles (Child Process 1)**
   - Manages socket connections for player equipment
   - Handles real-time updates of bullet counts and HP
   - Ensures synchronization between components

2. **Component Handlers (Child Processes 2-7)**
   Each handler process manages a specific component type:
   - **Gun Handler**: 
     - Processes shooting actions
     - Updates ammunition counts
     - Manages trigger events
   
   - **Vest Handler**:
     - Detects and processes hit registration
     - Updates player health status
     - Manages damage calculations
   
   - **Glove Handler**:
     - Processes motion data at 20Hz
     - Forwards data to HW Accelerator
     - Manages gesture recognition pipeline

3. **HW Accelerator (Child Processes 8-9)**
   - Dedicated process per player
   - Handles gesture recognition acceleration
   - Manages hardware-level motion processing

#### Process 2: Game Engine
The central game logic coordinator responsible for:
- Maintaining current game state
- Processing player actions from action_queue
- Updating game signals based on events
- Communicating with evaluation server
- Managing hardware component state updates

#### Process 3: Eval Client
Handles all evaluation server communications:
- Implements AES encryption for data security
- Manages game state verification
- Processes server responses
- Updates game engine with verified states

#### Process 4: MQTT Client
Manages real-time communication through:
- HiveMQ broker connection management
- Subscription to "LaserTag/OppInFrame" topic
- Game state publishing to "LaserTag/GameState"
- Real-time visualizer updates

#### Process 5: Console Interface
Provides system monitoring through:
- Real-time component status display
- Action history tracking
- Game state visualization
- System log management

### Inter-Process Communication
The system utilizes multiple communication mechanisms:
- Multiprocessing queues for asynchronous data transfer
- Shared arrays for real-time state management
- Socket connections for external communications
- MQTT for visualization updates
![Console Interface Diagram](./Image_Assets/console_interface.png)
*Figure: Inter-process communication showcased in the console interface*

This architecture ensures robust gameplay management while maintaining clear separation of concerns between different system components.

## Hardware Sensors Design and Implementaion
### List of Technical Components
Here are the main components used in the system:

| Component | Use |
|-----------|-----|
| DFR0339 Bluno Beetle | Receives sensor data and transmits to relays |
| MPU6050 (GY-521) | source of Linear and Gyroscopic data for gestures associated with Shield, Grenade, Reload, and Logout Move; Placed on player's action glove |
| IR Transmitter and Receiver | Transmitter on gun for laser shots simulation; Receiver on vests for shot detection |
| Piezo Buzzer | Provides audio feedback for both gun and vest |
| TM1637 4 Digit 7-Segment | Display on vest showing opponent's health |
| Trigger Button | On gun to enable IR signal emission for shots |
| Apparels | Vest, Glove, and Gun |

### Pin Configurations

#### Bluno Beetle to MPU Connection
| Pin on DFR0339 Bluno Beetle | Pin on MPU-6050 |
|-----------------------------|--------------------|
| 5V | VCC |
| GND | GND |
| A5 | SCL |
| A4 | SDA |

#### Bluno Beetle, IR Transmitter, Switch, Piezo Buzzer Connection
| Pin on DFR0339 Bluno Beetle | Pin on IR Transmitter | Pin on Switch | Pin on Piezo Buzzer |
|-----------------------------|----------------------|---------------|-------------------|
| 5V | VCC | - | - |
| GND | GND | GND | GND |
| D2 | - | VCC | - |
| D3 (PWM) | OUT | - | - |
| D5 (PWM) | - | - | VCC |

#### Bluno Beetle, IR Receiver, TM1637, Piezo Buzzer Connection
| Pin on DFR0339 Bluno Beetle | Pin on IR Receiver | Pin on TM1637 | Pin on Piezo Buzzer |
|-----------------------------|-------------------|---------------|-------------------|
| 5V | VCC | VCC | - |
| GND | GND | GND | GND |
| D2 | - | DIO | - |
| D3 (PWM) | OUT | - | - |
| D4 (PWM) | - | CLK | - |
| D5 (PWM) | - | - | OUT |

### Operating Voltages
| Component | Operating Voltage |
|-----------|------------------|
| DFR0339 Bluno Beetle | 5V |
| MPU-6050 | 2.375V - 3.46V |
| IR Transmitter | 1.2V |
| IR Receiver | 2.7V - 5.0V |
| Piezo Buzzer | 1.5V - 2.4V |
| TM1637 4 Digit 7 Segment Display | 3.3V - 5V |

### Libraries and Implementation
The system uses the following libraries in C++:
1. Glove: `<Wire.h>` and `<MPU6050.h>` for I2C communication
2. Gun: `<IRremote.hpp>` for IR signal transmission
3. Vest: `<IRremote.h>` and `<TM1637Display.h>` for IR reception and display

### Circuit Schematics
![Connection Between Bluno Beetle and MPU Sensor](./Image_Assets/conn_beetle_mpu.png)
*Circuit connections between Bluno Beetle microcontroller and MPU Sensor*

![Connection Between Bluno Beetle, IR-transmitter, Piezo Buzzer, and Push Button](./Image_Assets/conn_beetle_trans_buzzer_button.png)
*Circuit connections between Bluno Beetle microcontroller, IR Transmitter Piezo Buzzer, and Push Button*

![Connection Between Bluno Beetle, IR Receiver, and LED Strip](./Image_Assets/conn_beetle_receiver_led_strip.png)
*Circuit connections between Bluno Beetle microcontroller, IR Receiver and LED Strip*

### Implementation Details

#### Glove Implementation
- Uses I2C communication through Wire.h
- Extracts X, Y, Z axes data from MPU6050 for both accelerometer and gyroscope
- Combines two registers per axis to get correct values

#### Gun Implementation
- Emits unique IR signals per player using `IRSender.sendNEC(address,command,repeats)`
- Piezo buzzer provides audio feedback for successful shots and empty ammo

#### Vest Implementation
- Constantly receives and decodes IR signals using `IrReceiver.decode()`
- Validates signals based on player-specific commands
- Updates health display on TM1637
- Provides audio feedback for successful hit registration

#### Issues and Solutions
A key issue encountered during integration was the vest's inability to simultaneously receive data from both Serial (bluetooth) and IR Receiver. This was resolved by reinitializing the IR Receiver after bluetooth data reception using `IrReceiver.begin(IR_RCV_PIN)`.

