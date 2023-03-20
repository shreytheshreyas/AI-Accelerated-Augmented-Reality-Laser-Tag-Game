from socket import *
from sshtunnel import open_tunnel

soc_tunnel = open_tunnel(
    ("stu.comp.nus.edu", 22),
    ssh_username="kaijiel",
    remote_bind_address=("192.168.95.236", 22),
    block_on_close=False,
)
soc_tunnel.start()
print("Connected to SOC tunnel")

ultra96_tunnel = open_tunnel(
    ssh_address_or_host=("127.0.0.1", soc_tunnel.local_bind_port),
    remote_bind_address=("127.0.0.1", 2105),
    ssh_username="xilinx",
    block_on_close=False,
)
ultra96_tunnel.start()
print(ultra96_tunnel.local_bind_port)
print("Connected to Ultra96 tunnel")

serverName = "localhost"
serverPort = 2105
clientSocket = socket(AF_INET, SOCK_STREAM)
# clientSocket.connect((serverName, soc_tunnel.local_bind_port))
clientSocket.connect((serverName, ultra96_tunnel.local_bind_port))
message = input("Enter a message: ")
clientSocket.send(message.encode("utf8"))
receivedMsg = clientSocket.recv(2048)
print("from server:", receivedMsg.decode())
clientSocket.close()
