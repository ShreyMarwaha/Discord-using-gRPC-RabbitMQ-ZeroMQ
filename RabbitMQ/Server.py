import uuid
import pika
import sys
import os
import util
import json
import uuid


config = json.load(open('registryServer_config.json'))


def main():
    channel = util.connect(config['host'], config['port'])
    channel.queue_declare(queue='servers')

    unique_id = str(uuid.uuid1())
    message = unique_id

    channel.basic_publish(
        exchange='', routing_key='servers', body=message)
    print(" [x] Sent", message)

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

    # channel.basic_consume(
    #     queue='servers', on_message_callback=callback, auto_ack=True)
    # channel.start_consuming()

# print(' [*] Waiting for messages. To exit press CTRL+C')
# channel.start_consuming()
# print('this is blocking')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exiting...')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
