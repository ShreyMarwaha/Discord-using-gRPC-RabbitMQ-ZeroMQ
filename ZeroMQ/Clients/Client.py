import random
import time
import zmq
import json
import uuid

config = json.load(open("./config.json"))
unique_id = str(uuid.uuid1())
addressIP = "localhost"
addressPort = str(random.randint(1000, 9999))
SERVERS = []

# -------------------------------------------------------------------
# Function Definitions - Outgoing Functions
def GetServerList():
    global SERVERS
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://"+ str(config["registry_server_host"]) +":"+ str(config["registry_server_port"]))

    socket.send_string(f"REQUEST_SERVER_LIST, IP:{addressIP}, PORT:{addressPort}")
    l = socket.recv().decode('utf-8')
    SERVERS = l[2:-2].split("', '")
    
    for i in range(len(SERVERS)):
        print(f"{i+1}. {SERVERS[i]}")

def JoinServer(creds):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://"+ creds[creds.index("-")+2:])

    socket.send_string(f"JOIN_SERVER, UUID:{unique_id}")
    message = socket.recv()
    print(f"{message.decode('utf-8')}")

def LeaveServer(creds):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://"+ creds[creds.index("-")+2:])

    socket.send_string(f"LEAVE_SERVER, UUID:{unique_id}")
    message = socket.recv()
    print(f"{message.decode('utf-8')}")

def PublishArticle(creds):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://"+ creds[creds.index("-")+2:])
    time.sleep(1)

    print("Choose Article Type:")
    print("1. SPORTS")
    print("2. FASHION")
    print("3. POLITICS")
    print("Enter your choice:")
    c = int(input())
    print("Enter Article Author:")
    author = str(input())
    print("Enter Article Content:")
    content = str(input())
    
    if c == 1:
        socket.send_string(f"PUBLISH_ARTICLE, UUID:{unique_id}, TYPE:SPORTS, AUTHOR:{author}, CONTENT:{content}")
    elif c == 2:
        socket.send_string(f"PUBLISH_ARTICLE, UUID:{unique_id}, TYPE:FASHION, AUTHOR:{author}, CONTENT:{content}")
    elif c == 3:
        socket.send_string(f"PUBLISH_ARTICLE, UUID:{unique_id}, TYPE:POLITICS, AUTHOR:{author}, CONTENT:{content}")
    else:
        socket.send_string(f"PUBLISH_ARTICLE, UUID:{unique_id}, TYPE: , AUTHOR:{author}, CONTENT:{content}")
    
    time.sleep(1)
    message = socket.recv()
    print(f"{message.decode('utf-8')}")

def GetArticles(creds):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://"+ creds[creds.index("-")+2:])

    print("ARTICLE SEARCH PARAMETERS (type 0 to leave blank)")
    print("Choose Article Type:")
    print("1. SPORTS")
    print("2. FASHION")
    print("3. POLITICS")
    print("Enter your choice:")
    c = int(input())
    print("Enter Article Author:")
    author = str(input())
    print("Enter Article Content:")
    content = str(input())
    print("Search for Articles from Date (dd/mm/yyyy):")
    date = str(input())
    
    if c == 0:
        socket.send_string(f"GET_ARTICLES, UUID:{unique_id}, TYPE:0, AUTHOR:{author}, CONTENT:{content}, DATE:{date}")
    elif c == 1:
        socket.send_string(f"GET_ARTICLES, UUID:{unique_id}, TYPE:SPORTS, AUTHOR:{author}, CONTENT:{content}, DATE:{date}")
    elif c == 2:
        socket.send_string(f"GET_ARTICLES, UUID:{unique_id}, TYPE:FASHION, AUTHOR:{author}, CONTENT:{content}, DATE:{date}")
    elif c == 3:
        socket.send_string(f"GET_ARTICLES, UUID:{unique_id}, TYPE:POLITICS, AUTHOR:{author}, CONTENT:{content}, DATE:{date}")
    else:
        socket.send_string(f"GET_ARTICLES, UUID:{unique_id}, TYPE: , AUTHOR:{author}, CONTENT:{content}, DATE:{date}")
    
    message = socket.recv().decode('utf-8')
    
    l = message[2:-2].split("', '")
    if l[0] == "FAI":
        print("FAIL")
        return
    elif l[0] == "":
        print("NO ARTICLES FOUND")
        return
    else:
        for i in range(len(l)):
            print(f"{i+1} {l[i]}")
# -------------------------------------------------------------------

if __name__ == "__main__":
    print(f"CLIENT STARTED AT {addressIP}:{addressPort}")
    while True:
        print("-------------------------------------------------------------------")
        print("MENU")
        print("1. Request Server List")
        print("2. Join Server")
        print("3. Leave Server")
        print("4. Get Server Articles")
        print("5. Publish Article on Server")
        print("6. Exit")
        print("Enter your choice:")
        choice = int(input())
        print("-------------------------------------------------------------------")

        if choice == 1:
            print(f"REQUESTING SERVER LIST FROM REGISTRY SERVER AT {config['registry_server_host']}:{config['registry_server_port']}")
            GetServerList()

        elif choice == 2:
            print(f"REQUESTING SERVER LIST FROM REGISTRY SERVER AT {config['registry_server_host']}:{config['registry_server_port']}")
            GetServerList()

            print("Enter server number:")
            c = int(input())
            JoinServer(SERVERS[c-1])

        elif choice == 3:
            print(f"REQUESTING SERVER LIST FROM REGISTRY SERVER AT {config['registry_server_host']}:{config['registry_server_port']}")
            GetServerList()

            print("Enter server number:")
            c = int(input())
            LeaveServer(SERVERS[c-1])

        elif choice == 4:
            print(f"REQUESTING SERVER LIST FROM REGISTRY SERVER AT {config['registry_server_host']}:{config['registry_server_port']}")
            GetServerList()

            print("Enter server number:")
            c = int(input())
            GetArticles(SERVERS[c-1])

        elif choice == 5:
            print(f"REQUESTING SERVER LIST FROM REGISTRY SERVER AT {config['registry_server_host']}:{config['registry_server_port']}")
            GetServerList()

            print("Enter server number:")
            c = int(input())
            PublishArticle(SERVERS[c-1])

        elif choice == 6:
            print("EXITING...")
            exit()

        else:
            print("INVALID CHOICE. TRY AGAIN!")