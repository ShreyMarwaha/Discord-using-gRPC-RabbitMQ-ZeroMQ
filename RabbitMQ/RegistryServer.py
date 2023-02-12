import pika
import os
import sys
import util
import json
import ast
# This is basically a consumer

config = json.load(open("config.json"))
SERVERS = []
channel = util.connect(config["host"], config["port"])


def getServerList():
    list_message = {"from": "regserver", "id": "regserver",
                    "function": "GetServerList"}
    msg = ''
    for server in SERVERS:
        _ = '#'.join(server)
        msg += _ + ','
    list_message["message"] = msg[:-1]
    # uuid#address,uuid#address
    return json.dumps(list_message)


def handle_Register(body):
    print(" [x] JOIN REQUEST FROM %r" % body["address"])
    if len(SERVERS) < config['max_servers']:
        SERVERS.append([body["id"], body["address"]])
        print(" [x] Server List: %r" % SERVERS)
        print(" [x] Load: %r/%r" % (len(SERVERS), config['max_servers']))
        message = {"from": "regserver", "id": "regserver",
                   "message": "success"}
        channel.basic_publish(
            exchange="", routing_key=body["id"], body=json.dumps(message))
    else:
        print(" [x] Server Registration Failed %r" % body["id"])
        message = {"from": "regserver", "id": "regserver",
                   "message": "failed", "reason": "server full"}
        channel.basic_publish(
            exchange="", routing_key=body["id"], body=json.dumps(message))


def main():
    channel.queue_declare(queue="regserver")

    def callback_server(ch, method, properties, body):
        body = json.loads(body.decode('utf-8'))
        if body["from"] == "server":
            if body["function"] == "Register":
                handle_Register(body)
            else:
                print(" [x] Unsupported Request from %r" % body["address"])
        elif body["from"] == "client":
            if body["function"] == "GetServerList":
                print(" [x] SERVER LIST REQUEST FROM %r" % body["address"])
                channel.basic_publish(
                    exchange="", routing_key=body["id"], body=getServerList())
            else:
                print(" [x] Unsupported Request from %r" % body["address"])
        else:
            print(" [x] Unrecognized Request from %r" % body["address"])

    channel.basic_consume(
        queue="regserver", on_message_callback=callback_server, auto_ack=True)
    print(" [*] Name: Registry Server,  Status: Online. \nTo exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
