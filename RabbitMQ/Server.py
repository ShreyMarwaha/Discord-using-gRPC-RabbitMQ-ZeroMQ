import uuid
import sys
import os
import util
import json
from datetime import date, datetime

config = json.load(open("config.json"))
channel = util.connect(config["host"], config["port"])

unique_id = str(uuid.uuid1())
PORT = channel.connection._impl._transport._sock.getsockname()[1]
address = "localhost:" + str(PORT)

CLIENTELE = []
ARTICLES = []


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
                   "function": "JoinServer", "message": "failed", "reason": "server full"}
        channel.basic_publish(
            exchange="", routing_key=body["id"], body=json.dumps(message))


def handle_LeaveServer(body):
    global CLIENTELE
    print(" [x] LEAVE REQUEST FROM %r" % body["id"])
    CLIENTELE.remove(body["id"])
    print(" [x] Clientele: %r" % CLIENTELE)
    message = {"from": "server", "id": unique_id, "address": address, "function": "LeaveServer",
               "message": "success"}
    channel.basic_publish(
        exchange="", routing_key=body["id"], body=json.dumps(message))


def handle_GetArticles(body):
    print(" [x] ARTICLES REQUEST FROM %r" % body["id"])
    articles_list = []
    requested_date = datetime.strptime(
        body["article"]["date"], "%Y-%m-%d").date()
    for article in ARTICLES:
        if article.date >= requested_date:
            if (len(body["article"]["author"]) == 0 or article.author == body["article"]["author"]) and (len(body["article"]["type"]) == 0 or article.type == body["article"]["type"]):
                articles_list.append({"type": article.type, "author": article.author,
                                      "date": str(article.date), "content": article.content})
    message = {"from": "server", "id": unique_id, "address": address,
               "function": "GetArticles", "message": articles_list}
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


def main():
    print(" [*] Name: Server,  Status: Online. \nTo exit press CTRL+C")
    channel.queue_declare(queue=unique_id)
    register()

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

    channel.basic_consume(
        queue=unique_id, on_message_callback=callback_client, auto_ack=True)
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
