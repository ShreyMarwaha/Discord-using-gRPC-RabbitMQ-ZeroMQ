import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

def Register(serverIP, serverPort):    
    socket.send_string(f"IP:{serverIP}, PORT:{serverPort}")
    message = socket.recv()
    print(f"{message.decode('utf-8')}")

if __name__ == "__main__":
    Register("LOCALHOST", "2000")