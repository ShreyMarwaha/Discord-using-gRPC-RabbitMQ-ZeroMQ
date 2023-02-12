import random
import zmq
import json

config = json.load(open("./config.json"))
addressIP = "localhost"
addressPort = str(random.randint(1000, 9999))

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://"+ str(config["registry_server_host"]) +":"+ str(config["registry_server_port"]))

# -------------------------------------------------------------------
# Function Definitions
def Register():    
    socket.send_string(f"IP:{addressIP}, PORT:{addressPort}")
    message = socket.recv()
    print(f"{message.decode('utf-8')}")
# -------------------------------------------------------------------

if __name__ == "__main__":
    print(f"SERVER STARTED AT {addressIP}:{addressPort}")
    print(f"REGISTERING WITH REGISTRY SERVER AT {config['registry_server_host']}:{config['registry_server_port']}")
    Register()