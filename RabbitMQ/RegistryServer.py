import pika
import os
import sys
import util
import json
# This is basically a consumer

config = json.load(open('registryServer_config.json'))

# stores server's uuid
server_list = []


def main():
    channel = util.connect(config['host'], config['port'])
    channel.queue_declare(queue='servers')
    channel.queue_declare(queue='clients')

    def callback_client(ch, method, properties, body):
        print(" [x] Server List Request Received %r" % body)
        message = 'here is the list'

        channel.basic_publish(
            exchange='', routing_key=body.decode(), body=message)
        print(" [x] Sent", message)
    # ch.basic_ack(delivery_tag=method.delivery_tag)

    def callback_server(ch, method, properties, body):
        print(" [x] Rregistration Request %r" % body)
        server_list.append(body)
        print(server_list)

    channel.basic_consume(
        queue='clients', on_message_callback=callback_client, auto_ack=True)

    channel.basic_consume(
        queue='servers', on_message_callback=callback_server, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exiting...')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
