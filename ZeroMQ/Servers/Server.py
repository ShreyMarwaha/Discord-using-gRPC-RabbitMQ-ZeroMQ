from datetime import datetime
import random
import zmq
import json

config = json.load(open("./config.json"))
addressIP = "localhost"
addressPort = str(random.randint(1000, 9999))
CLIENTELE = []
ARTICLES = []

class article:
    # class to store article, contains type, author, time, content
    def __init__(self, type, author, content):
        self.type = type
        self.author = author
        self.time = datetime.today()
        self.content = content

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://"+ str(config["registry_server_host"]) +":"+ str(config["registry_server_port"]))
server_socket = context.socket(zmq.REP)
server_socket.bind("tcp://*:"+str(addressPort))

# -------------------------------------------------------------------
# Function Definitions - Outgoing Functions
def Register():    
    socket.send_string(f"IP:{addressIP}, PORT:{addressPort}")
    message = socket.recv()
    print(f"{message.decode('utf-8')}")

# Function Definitions - Incoming Functions
def JoinServer(id):
    if len(CLIENTELE) < config["max_clients_per_server"] and id not in CLIENTELE:
        CLIENTELE.append(id)
        return b"SUCCESS"
    else:
        return b"FAIL"

def LeaveServer(id):
    if id in CLIENTELE:
        CLIENTELE.remove(id)
        return b"SUCCESS"
    else:
        return b"FAIL"

def PublishArticle(id, msg):
    if id in CLIENTELE:
        type = msg[msg.index(b", TYPE:") + 7 : msg.index(b", AUTHOR")].decode("utf-8")
        author = msg[msg.index(b", AUTHOR:") + 9 : msg.index(b", CONTENT")].decode("utf-8")
        content = msg[msg.index(b", CONTENT:") + 10 : ].decode("utf-8")

        ARTICLES.append(article(type, author, content))
        return b"SUCCESS"
    else:
        return b"FAIL"
    
def GetArticles(id):
    if id in CLIENTELE:
        art = []
        for i, articles in enumerate(ARTICLES):
            art.append(f"TYPE: {articles.type}, AUTHOR: {articles.author}, TIME: {articles.time}, CONTENT: {articles.content}")
        return art
    else:
        return b"FAIL"
# -------------------------------------------------------------------

if __name__ == "__main__":
    print(f"SERVER STARTED AT {addressIP}:{addressPort}")
    print(f"REGISTERING WITH REGISTRY SERVER AT {config['registry_server_host']}:{config['registry_server_port']}")
    Register()

    while True:
        message = server_socket.recv()

        # Join Server
        if(message.startswith(b"JOIN_SERVER")):
            uuid = message[message.index(b":") + 1 : ].decode("utf-8")
            print(f"JOIN REQUEST FROM CLIENT {uuid}")
            res = JoinServer(uuid)
            server_socket.send(res)
        
        # Leave Server
        elif(message.startswith(b"LEAVE_SERVER")):
            uuid = message[message.index(b":") + 1 : ].decode("utf-8")
            print(f"LEAVE REQUEST FROM CLIENT {uuid}")
            res = LeaveServer(uuid)
            server_socket.send(res)
        
        # Publish Article
        elif(message.startswith(b"PUBLISH_ARTICLE")):
            uuid = message[message.index(b":") + 1 : message.index(b", TYPE")].decode("utf-8")
            print(f"ARTICLE PUBLISH REQUEST FROM CLIENT {uuid}")
            res = PublishArticle(uuid, message)
            server_socket.send(res)

        # Get Articles
        elif(message.startswith(b"GET_ARTICLES")):
            uuid = message[message.index(b":") + 1 : ].decode("utf-8")
            print(f"ARTICLES REQUEST FROM CLIENT {uuid} FOR ALL ARTICLES")
            res = str(GetArticles(uuid))
            server_socket.send_string(res)