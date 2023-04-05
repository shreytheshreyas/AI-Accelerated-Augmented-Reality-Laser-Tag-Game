# Flow
1. Create python program running on Ultra96 that connects
    1. via TCP to:
        1. Visualisers
        2. Eval Server
        3. Laptop (relay nodes) for component state and sensor data
    2. via Wired Connection
        1. Hardware Accelerator for machine learning

# Design
1 Process to handle the IMU data coming from user and pass that on to ML AI
1 Process to take in updates to game state based on:
1. Gun Game State
2. Vest Game State
3. Glove Action from ML AI

1 thread to receive data from each of the 3 components and add desired game state to queue
1 game engine thread that takes desired game state from queue and update the overal game state

# Issues


# Roadmap
## Ultra96
Eval Client that sends data to eval_server
Server that recieves data from laptop (relay node)
Threaded environment to combine both functionalities simulataneously

## Laptop
Stub for beetle program on laptop
Client to send data to ultra96



# Other Info
* Ensures AI Logic, Reponse Time, and Game State is correct
* Don't set thread priorities, let python handle it. might cause locks
* just use queues to control the flow between threads, dont need to use mutex or locks
* Unrestricted - no eval server
* Shield timer will always wrong different between eval server and - so not penalised for health effects/ shield time but need to update post action to match eval server time

# First check in (Week 5)
* Your code framework should be more or less in place.
* eval_client should be working [done]
* laptop relay: Tunnel established. [done]
* Game Engine to Visualizer connection established. []
* Scheduling of threads/processes should be in place [done]

# Full individual system check (Week 6)
1. Socket communications between Ultra96 to evaluation server (Both client and server running on your laptop, via localhost): [Live + Video]
    * Show successful communications with dummy data [2]
2. Communications between laptop and Ultra96 [Live + Video]
    * Explain and demo ssh tunnelling to Ultra96 [2]
    * Walk through code and explain concurrency/threading of code on laptop and Ultra96 (if any) [2]
    * Demo successful communications between ONE laptop to Ultra96 with dummy data [3]
3. Communications between Ultra96 and Visualizer (on phone) [Live + Video]
    * Explain the protocol for communication [2]
    * Explain and Demo successful communications between Ultra96 and Visualizer with dummy data [3]
4. In addition to individual communication, you should also show a single complete pipeline (as described below) [6] [Live + Video]
    * At the Relay laptop, accept user input via the keyboard.
        * At each keystroke, send a random dummy packet to Ultra96.
    * At Ultra96, when you receive a dummy packet from the Relay laptop.
        * Generate a random AI event (Grenade, shield, reload or shoot) for players
        * Pass the information to the Eval server and Visualizer
        * When the action is Grenade, send a Query request to the Visualizer to see if the opponent is in the field of view; and get the response.


# Game Engine flow
2 different game mode - eval and normal

## Normal Mode 
Each action should just update the stats accordinginly regardless of the other player's actions
# CANNOT
Vest hit depends on whether other player still has bullets, since the user can keep spamming hits


## Eval Mode
Each action updates stats individually but there should be a turn manager, so if a bunch of actions fulfilled then turn is considered complete and an action is sent to eval_server
