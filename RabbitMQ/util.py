import pika


def connect(ip, port):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=ip))
    return connection.channel()
