import zmq
import json

config = json.load(open("./config.json"))
SERVERS = []

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:"+str(config["registry_server_port"]))

# -------------------------------------------------------------------
# Function Definitions - Incoming Functions
def Register(ip, port):
    if len(SERVERS) < config["max_servers"]:
        SERVERS.append("ServerName" + str(len(SERVERS)+1) + " - " + ip + ":" + port)
        return b"SUCCESS"
    else:
        return b"FAIL"

def GetServerList():
    if len(SERVERS) > 0:
        return str(SERVERS).encode("utf-8")
    else:
        return b"FAIL"
# -------------------------------------------------------------------

while True:
    message = socket.recv()

    # Register Server
    if(message.startswith(b"IP:")):
        ip = message[message.index(b":") + 1 : message.index(b",")].decode("utf-8")
        port = message[message.index(b",") + 7 : ].decode("utf-8")
        m = ip + ":" + port

        print(f"JOIN REQUEST FROM SERVER {m}")
        res = Register(ip, port)
        socket.send(res)
        
    # Server List Requested
    elif(message.startswith(b"REQUEST_SERVER_LIST")):
        ip = message[message.index(b":") + 1 : message.index(b", PORT")].decode("utf-8")
        port = message[message.index(b"PORT:") + 5 : ].decode("utf-8")
        m = ip + ":" + port

        print(f"SERVER LIST REQUEST FROM CLIENT {m}")
        res = GetServerList()
        socket.send(res)