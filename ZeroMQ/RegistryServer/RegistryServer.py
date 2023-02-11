import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

def Register(ip, port): 
    f1 = open("serverList", "w+")
    f2 = open("config", "r")
    f3 = open("serverList", "w")
    l1 = f1.readline()
    l2 = f2.readline()
    n = -1
    print(f"l1 = {l1}")
    if len(l1) == 0:
        n = 0
        f1.write(f"0|")
        l1 = "0|"
    else:
        n = int(l1[:l1.index("|")])
    MAXSERVERS = int(l2[l2.index(":")+1:l2.index("|")])
    print(f"n = {n}")
    if n < MAXSERVERS:
        f3.write(f"{n+1}|"+l1[l1.index("|")+1:]+f"{ip}:{port}|")
        f1.close()
        f2.close()
        f3.close()
        return b"SUCCESS"
    else:
        return b"FAILED"

while True:
    message = socket.recv()
    if(message.startswith(b"IP:")):
        ip = message[message.index(b":") + 1 : message.index(b",")].decode("utf-8")
        port = message[message.index(b",") + 7 : ].decode("utf-8")
        m = ip + ":" + port
        print(f"JOIN REQUEST FROM {m}")
        res = Register(ip, port)
        socket.send(res)