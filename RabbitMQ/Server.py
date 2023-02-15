import threading
from time import sleep
import uuid
import sys
import os
import pika
import json
from datetime import date, datetime
import util

config = json.load(open("config.json"))
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue="regserver")

unique_id = str(uuid.uuid1())
PORT = channel.connection._impl._transport._sock.getsockname()[1]
address = "localhost:" + str(PORT)

CLIENTELE = []
ARTICLES = []

AVAILABLE_SERVERS = []
JOINED_SERVERS = []


class article:
    # class to store article, contains type, author, time, content
    def __init__(self, type, author, content):
        self.type = type
        self.author = author
        self.date = date.today()
        self.content = content


def to_unicode_string(s):
    try:
        # Try to decode the string as UTF-8
        return s.decode('utf-8')
    except:
        # If that fails, try to decode as ASCII
        return s.decode('ascii', 'ignore')


def register():
    message = {"from": "server", "id": unique_id,
               "function": "Register", "address": address}
    try:
        channel.basic_publish(
            exchange="", routing_key="regserver", body=json.dumps(message))
        print(" [x] Sent Register request to Registry Server")
    except Exception as e:
        print(" [x] Error: %r" % e)


def handle_JoinServer(body):
    print(" [x] JOIN REQUEST FROM %r" % body["id"])
    if len(CLIENTELE) < config["max_clients_per_server"]:
        if body["id"] in CLIENTELE:
            print(
                " [x] Client Registration Failed %r. Reason: Client already registered" % body["id"])
            message = {"from": "server", "id": unique_id, "address": address,
                       "function": "JoinServer", "message": "failed", "reason": "already registered"}
            channel.basic_publish(
                exchange="", routing_key=body["id"], body=json.dumps(message))
        else:
            CLIENTELE.append(body["id"])
            print(" [x] Client Registered %r" % body["id"])
            print(" [x] Clientele: %r" % CLIENTELE)
            print(" [x] Load: %r/%r" %
                  (len(CLIENTELE), config["max_clients_per_server"]))

            message = {"from": "server", "id": unique_id, "address": address,
                       "function": "JoinServer",    "message": "success"}
            channel.basic_publish(
                exchange="", routing_key=body["id"], body=json.dumps(message))
    else:
        print(" [x] Client Registration Failed %r" % body["id"])
        message = {"from": "server", "id": unique_id, "address": address,
                   "function": "JoinServer", "message": "failed", "reason": "server full", "type": "reply"}
        channel.basic_publish(
            exchange="", routing_key=body["id"], body=json.dumps(message))


def handle_LeaveServer(body):
    global CLIENTELE
    print(" [x] LEAVE REQUEST FROM %r" % body["id"])
    CLIENTELE.remove(body["id"])
    print(" [x] Clientele: %r" % CLIENTELE)
    message = {"from": "server", "id": unique_id, "address": address, "function": "LeaveServer",
               "message": "success", "type": "reply"}
    channel.basic_publish(
        exchange="", routing_key=body["id"], body=json.dumps(message))


# get_articles_handler = {id1: {reply: {res1, res2, res3}, message: "article1, artile2, ..."}, id2: {res1, res4}}
get_articles_handler = {}


def handle_GetArticles(body):
    global get_articles_handler

    print(" [x] ARTICLES REQUEST FROM %r" % body["id"])
    if body["id"] in CLIENTELE:
        get_articles_handler[body["id"]] = {"reply": set(), "message": ""}
    for server in JOINED_SERVERS:
        # if not received reply from any SERVER, then ask
        if server not in get_articles_handler[body["id"]]["reply"]:
            message = {"from": "server", "id": unique_id, "address": address,
                       "function": "GetArticles", "type": "request"}
            channel.basic_publish(
                exchange="", routing_key=server, body=json.dumps(message))
            print(" [x] Articles Request Sent to %r" % server)

    articles_list = []
    requested_date = datetime.strptime(
        body["article"]["date"], "%Y-%m-%d").date()
    for article in ARTICLES:
        if article.date >= requested_date:
            if (len(body["article"]["author"]) == 0 or article.author == body["article"]["author"]) and (len(body["article"]["type"]) == 0 or article.type == body["article"]["type"]):
                articles_list.append({"type": article.type, "author": article.author,
                                      "date": str(article.date), "content": article.content})
    message = {"from": "server", "id": unique_id, "address": address,
               "function": "GetArticles", "message": articles_list, "type": "reply"}
    channel.basic_publish(
        exchange="", routing_key=body["id"], body=json.dumps(message))
    print(" [x] Articles Sent to %r" % body["id"])


def handle_PublishArticle(body):
    global CLIENTELE, ARTICLES
    print(" [x] ARTICLES PUBLISH FROM %r" % body["id"])
    if body["id"] in CLIENTELE:
        ARTICLES.append(
            article(body["article"]["type"], body["article"]["author"], body["article"]["content"][:200]))
        print(" [x] Article Published by%r" % body["id"])

        message = {"from": "server", "id": unique_id, "address": address, "function": "PublishArticle",
                   "message": "success"}
        channel.basic_publish(
            exchange="", routing_key=body["id"], body=json.dumps(message))
    else:
        print(" [x] Article Publish Failed by %r" % body["id"])
        message = {"from": "server", "id": unique_id, "address": address,
                   "function": "PublishArticle", "message": "failed"}

        channel.basic_publish(
            exchange="", routing_key=body["id"], body=json.dumps(message))


def server_functionality():
    def callback_client(ch, method, properties, body):
        body = json.loads(body.decode())

        if body["from"] == "client":
            if body["function"] == "JoinServer":
                handle_JoinServer(body)
            elif body["function"] == "LeaveServer":
                handle_LeaveServer(body)
            elif body["function"] == "GetArticles":
                handle_GetArticles(body)
            elif body["function"] == "PublishArticle":
                handle_PublishArticle(body)
            else:
                print(" [x] Invalid request from",
                      body["id"], ". Request:", body)

        elif body["from"] == "regserver":
            if body["message"] == "success":
                print(" [x] [SUCCESS] Server Registered Successfully")
            else:
                print(" [x] [FAIL] Registration Failed on RegServer")
                print("Exiting...")
                exit(0)
        elif body['from'] == 'server':
            if body["function"] == "JoinServer":
                if body["type"] == "request":
                    handle_JoinServer(body)
                else:
                    if body["message"] == "success":
                        print(" [x] Successfully joined server %r" %
                              body["id"])
                        JOINED_SERVERS.append(body["id"])
                    else:
                        print(" [x] Failed to join server. Reason:",
                              body["reason"])

            elif body["function"] == "LeaveServer":
                if body["type"] == "request":
                    handle_LeaveServer(body)
                else:
                    if body["message"] == "success":
                        print(" [x] Successfully left server %r" % body["id"])
                        JOINED_SERVERS.remove(body["id"])
                    else:
                        print(" [x] Failed to leave server.")

    channel.basic_consume(
        queue=unique_id, on_message_callback=callback_client, auto_ack=True)
    channel.start_consuming()


def server_joinOtherServer():
    while True:
        method_number, function = util.select_one_from_list(
            ["GetServerList", "JoinServer", "LeaveServer"], "Enter the method number")
        if method_number == -1:
            util.quit()

        elif method_number == 0:
            message = {"from": "server", "id": unique_id, "address": address,
                       "function": "GetServerList"}
            channel.basic_publish(
                exchange="", routing_key="regserver", body=json.dumps(message))
            print(" [x] GetServerList Request Sent")
            sleep(1)

        elif method_number == 1:
            if len(AVAILABLE_SERVERS) == 0:
                print(
                    "No servers available to join. Refresh the list by using `GetServerList`.")
                continue

            print("Here is the list of available servers:")
            server_num, server_id = util.select_one_from_list(
                AVAILABLE_SERVERS, "Enter the server number that you would like to join")
            if server_num == -1:
                continue

            message = {"from": "server", "id": unique_id,
                       "address": address, "function": "JoinServer", "type": "request"}
            channel.basic_publish(
                exchange="", routing_key=server_id, body=json.dumps(message))

        elif method_number == 2:
            if len(JOINED_SERVERS) == 0:
                print("You are not connected to any server.")
                continue

            print("Here is the list of available servers:")
            server_num, server_id = util.select_one_from_list(
                JOINED_SERVERS, "Enter the server number that you would like to join")
            if server_num == -1:
                continue

            message = {"from": "server", "id": unique_id,
                       "address": address, "function": "LeaveServer", "type": "request"}
            channel.basic_publish(
                exchange="", routing_key=server_id, body=json.dumps(message))

        else:
            print("Invalid method number")


def main():
    util.print_status("Server", unique_id, PORT)
    channel.queue_declare(queue=unique_id)
    register()

    # Create a thread to handle publishing messages
    publishing_thread = threading.Thread(
        target=lambda: server_joinOtherServer())

    # Create a thread to handle consuming messages
    server_main_thread = threading.Thread(target=server_functionality)
    # Start both threads
    server_main_thread.start()
    publishing_thread.start()

    # Wait for both threads to finish
    server_main_thread.join()
    publishing_thread.join()

    connection.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
