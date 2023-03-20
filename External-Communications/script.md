c14f3e809cb145569a13b7912611d549.s2.eu.hivemq.cloud
8883

cg4002b13
xilinxB13capstone

LaserTag/GameState
LaserTag/OppInFrame

{"opp": "p1", "inFrame": true}

comm between relay node and ultra96
relayserver component responsible
connected dictionary helps to ensure that only one component from each player is being connected to the server at each time
the end_queue is used for the processes of each connection to tell the connected component that it is no longer connected
the processes will write to the action_queue after an action has been recieved for the game engine to work on it

similar to the eval client, there is a receive function to receive communications via the socket and a send_plaintext function for replies.
note that no ecryption is needed here


following that we have 3 functions to handle the individual connections of different components


the gun function should recieve a shoot msg from the player and pass that information to the action queue)
the vest funtion should recieve a hit msg from the player and pass that information to the queue)

and lastly the glove connec


