import pika
import sys
import os


def connect(ip, port):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=ip))
    return connection.channel()


def select_one_from_list(arr, msg):
    print("\n\n"+msg+" (Exit with -1)")
    for i, ele in enumerate(arr):
        print(str(i) + ". " + ele)

    select = int(input("Select: "))
    while select < -1 or len(arr) <= select:
        print(select)
        print(" [x] Invalid Selection. Select in the range [-1, %r]" %
              (len(arr)-1))
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
        f" [*] NODE: {node},  STATUS: Online, ID:{id}, PORT:{port}\nTo exit press CTRL+C")


# proto = {
#     "from": "server" / "client",
#     "id": "1234",
#     "function": "register",
#     ??"message_type": "request" / "response",
#     "message": ""
# }

# def sendMsg(channel, msg, queue):
#     channel.queue_declare(queue=queue)
#     channel.basic_publish(
#         exchange='', routing_key=queue, body=msg)
#     print(" [x] Sent", msg, "to", queue)
