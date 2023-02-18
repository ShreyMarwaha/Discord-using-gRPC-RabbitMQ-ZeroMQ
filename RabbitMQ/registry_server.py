import util
import json

config = json.load(open("config.json", "r"))
SERVERS = []
channel = util.connect(config["host"], config["port"])


def getServerList():
    list_message = {"from": "regserver", "id": "regserver", "function": "GetServerList"}
    msg = ""
    for server in SERVERS:
        _ = "#".join(server)
        msg += _ + ","
    list_message["message"] = msg[:-1]
    # uuid#address,uuid#address
    return json.dumps(list_message)


def handle_Register(body):
    print(" [x] JOIN REQUEST FROM %r" % body["address"])
    message = {
        "from": "regserver",
        "id": "regserver",
        "message": "success",
        "function": "Register",
    }
    if len(SERVERS) < config["max_servers"]:
        SERVERS.append([body["id"], body["address"]])
        print(" [x] Server List: %r" % SERVERS)
        print(" [x] Load: %r/%r" % (len(SERVERS), config["max_servers"]))

    else:
        print(" [x] Server Registration Failed %r" % body["id"])
        message["message"] = "failed"
        message["reason"] = "server full"

    channel.basic_publish(exchange="", routing_key=body["id"], body=json.dumps(message))


def main():
    util.print_status("Registry Server", "regserver", config["port"])
    channel.queue_declare(queue="regserver")

    def callback_server(ch, method, properties, body):
        body = json.loads(body.decode("utf-8"))
        if body["from"] == "server" and body["function"] == "Register":
            handle_Register(body)
        elif body["function"] == "GetServerList":
            print(" [x] SERVER LIST REQUEST FROM %r" % body["address"])
            channel.basic_publish(
                exchange="", routing_key=body["id"], body=getServerList()
            )
        else:
            print(" [x] Unrecognized Request from %r" % body["address"])

    channel.basic_consume(
        queue="regserver", on_message_callback=callback_server, auto_ack=True
    )
    channel.start_consuming()


if __name__ == "__main__":
    try:
        util.print_node_type("regserver")
        main()
    except KeyboardInterrupt:
        util.quit()
