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

### System Architecture Diagram Illustration
{Include System Architecture Diagram}
This is a test
### Hardware Components Placement
{Drawing of harware components}
{Grid Picture of Gun, Vest}

### Main Processes
This system employs a multi-process architecture where parent and child processes communicate securely through multiprocessing queues and arrays. Below, we detail the core functionality of each parent process and its associated child processes.

1. **Relay Server Parent Process**
   - **Child Process 1**: Update Beetles
     - Tracks socket connections for players' guns and vests
     - Sends bullet and health-points data via socket connection
   
   - **Child Processes 2-7**: Handle Component Connections
     - Instantiated when a Relay Node connection is established and the initial message confirms the component type.
     - Processes component-specific messages:
       - Gun: Adds player and "shoot" to action_queue
       - Vest: Adds player and "hit" to action_queue
       - Glove: Sends 20Hz data points to HW Accel Process

   - **Child Processes 8-9**: HW Accelerator
     - Uploads bitstream using pynq library
     - Manages DMA buffers for each player
