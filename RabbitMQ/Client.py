import pika
import json
import util
import uuid

config = json.load(open('registryServer_config.json'))

channel = util.connect(config['host'], config['port'])

unique_id = str(uuid.uuid1())
print("unique_id:", unique_id)

channel.queue_declare(queue='clients')

message = unique_id
channel.basic_publish(exchange='', routing_key='clients', body=message)


def callback_server(ch, method, properties, body):
    print(" [x] Received %r" % body)


channel.queue_declare(queue=unique_id)
channel.basic_consume(
    queue=unique_id, on_message_callback=callable, auto_ack=True)
channel.start_consuming()
print(" [x] Sent", message)
