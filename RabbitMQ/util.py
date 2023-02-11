import pika


def connect(ip, port):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=ip))
    return connection.channel()


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
