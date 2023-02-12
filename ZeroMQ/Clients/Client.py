import random
import zmq
import json
import uuid

config = json.load(open("./config.json"))
unique_id = str(uuid.uuid1())
addressIP = "localhost"
addressPort = str(random.randint(1000, 9999))
serverlist = []

# -------------------------------------------------------------------
# Function Definitions
def GetServerList():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://"+ str(config["registry_server_host"]) +":"+ str(config["registry_server_port"]))

    socket.send_string(f"REQUEST_SERVER_LIST, IP:{addressIP}, PORT:{addressPort}")
    serverlist = socket.recv()
    print(f"{serverlist.decode('utf-8')}")
# -------------------------------------------------------------------

if __name__ == "__main__":
    print(f"CLIENT STARTED AT {addressIP}:{addressPort}")
    print(f"REQUESTING SERVER LIST FROM REGISTRY SERVER AT {config['registry_server_host']}:{config['registry_server_port']}")
    GetServerList()