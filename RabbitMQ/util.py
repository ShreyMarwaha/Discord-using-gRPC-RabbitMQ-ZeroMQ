import json
import pika
import sys
import os


def connect(ip, port):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=ip))
    return connection.channel()


def select_one_from_list(arr, msg):
    print("\n\n" + msg + " (Exit with -1)")
    for i, ele in enumerate(arr):
        print(str(i) + ". " + ele)

    select = int(input("Select: "))
    while select < -1 or len(arr) <= select:
        print(select)
        print(" [x] Invalid Selection. Select in the range [-1, %r]" % (len(arr) - 1))
        select = int(input("Select: "))

    if select >= 0:
        return select, arr[select]
    return -1, ""


def quit():
    print("Exiting...")
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)


def print_status(node, id, port):
    print(
        f" [*] NODE: {node},  STATUS: Online, ID:{id}, PORT:{port}\nTo exit press CTRL+C"
    )


class Message:
    def __init__(self, from_, id, type, address, function="", message="", reason=""):
        self.from_ = from_
        self.id = id
        self.function = function
        self.address = address
        self.type = type
        self.type = address
        self.message = message
        self.reason = reason

    def check_params(self):
        if (
            self.from_ == ""
            or self.id == ""
            or self.type == ""
            or self.function == ""
            or self.message == ""
            or self.address == ""
            or (self.message == "failed" and self.reason == "")
        ):
            return False
        return True

    def __json__(self):
        if self.check_params():
            message = {
                "from": self.from_,
                "id": self.id,
                "function": self.function,
                "type": self.type,
                "address": self.address,
                "message": self.message,
                "reason": self.reason,
            }
            return json.dumps(message)
        else:
            raise Exception("Message Parameters Missing")


def send(channel, routing_key, message_obj):
    channel.basic_publish(
        exchange="", routing_key=routing_key, body=message_obj.__json__()
    )


def print_node_type(node_type):
    if node_type == "client":
        print("_________ .__  .__               __   ")
        print("\\_   ___ \\|  | |__| ____   _____/  |_ ")
        print("/    \\  \\/|  | |  |/ __ \\ /    \\   __\\")
        print("\\     \\___|  |_|  \\  ___/|   |  \\  |  ")
        print(" \\______  /____/__|\\___  >___|  /__|  ")
        print("        \\/             \\/     \\/     ")
    elif node_type == "server":
        print("  _________                                ")
        print(" /   _____/ ______________  __ ___________ ")
        print(" \\_____  \\_/ __ \\_  __ \\  \\/ // __ \\_  __ \\")
        print(" /        \\  ___/|  | \\/\\   /\\  ___/|  | \\/")
        print("/_______  /\\___  >__|    \\_/  \\___  >__|   ")
        print("        \\/     \\/                 \\/   ")

    elif node_type == "regserver":
        print("__________                  _________             ")
        print("\\______   \\ ____   ____    /   _____/ ___________ ")
        print(" |       _// __ \\ / ___\\   \\_____  \\_/ __ \\_  __ \\")
        print(" |    |   \\  ___// /_/  >  /        \\  ___/|  | \\/")
        print(" |____|_  /\\___  >___  /  /_______  /\\___  >__|   ")
        print("        \\/     \\/_____/           \\/     \\/  ")
