import pika
import os
import sys
import util
import json
# This is basically a consumer

config = json.load(open('config.json'))
SERVERS = []
channel = util.connect(config['host'], config['port'])


def getServerList():
    message = ''
    for server in SERVERS:
        message += server + ','
    return message


def handle_Register(body):
    print(" [x] Rregistration Request %r" % body['id'])
    if len(SERVERS) < config.max_servers:
        SERVERS.append(body['id'])
        print(" [x] Server Registered %r" % body['id'])
        print(" [x] Server List: %r" % SERVERS)
        message = {"from": 'regserver', "id": 'regserver',
                   "message": "success"}
        channel.basic_publish(
            exchange='', routing_key=body[id], body=str(message))
    else:
        print(" [x] Server Registration Failed %r" % body['id'])
        message = {"from": 'regserver', "id": 'regserver',
                   "message": "failed"}
        channel.basic_publish(
            exchange='', routing_key=body[id], body=str(message))


def main():
    channel.queue_declare(queue='regserver')

    def callback_server(ch, method, properties, body):
        body = json.loads(body.decode())
        if body['from'] == 'server':
            if body['function'] == 'Register':
                handle_Register(body)
            else:
                print(" [x] Unsupported Request from %r" % body['id'])
        elif body['from'] == 'client':
            if body['function'] == 'GetServerList':
                print(" [x] Server list request from %r" % body['id'])
                channel.basic_publish(
                    exchange='', routing_key=body[id], body=getServerList())
            else:
                print(" [x] Unsupported Request from %r" % body['id'])
        else:
            print(" [x] Unrecognized Request from %r" % body['id'])

    channel.basic_consume(
        queue='regserver', on_message_callback=callback_server, auto_ack=True)
    print(' [*] Name: Registry Server,  Status: Online. \nTo exit press CTRL+C')
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
