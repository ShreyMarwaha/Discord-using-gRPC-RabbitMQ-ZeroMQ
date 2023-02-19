import threading
from time import sleep
import uuid
import sys
import os
import pika
import json
from datetime import date, datetime
import util
import time

config = json.load(open("config.json", "r"))
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue="regserver")

unique_id = str(uuid.uuid1())
PORT = channel.connection._impl._transport._sock.getsockname()[1]
address = "localhost:" + str(PORT)

CLIENTELE = set()
CLIENTELE_servers = set()
ARTICLES = {}  # {id: article}
AVAILABLE_SERVERS = []
JOINED_SERVERS = set()


class Article:
    # class to store article, contains type, author, time, content
    def __init__(self, type, author, content, datetime=datetime.now()):
        self.type = type
        self.author = author
        self.datetime = datetime
        self.content = content


def generate_article_hash(article):
    return str(article.datetime) + str(article.author) + str(article.type)


def register():
    message = {
        "from": "server",
        "id": unique_id,
        "function": "Register",
        "address": address,
        "type": "request",
    }
    try:
        channel.basic_publish(
            exchange="", routing_key="regserver", body=json.dumps(message)
        )
        print(" [x] Sent Register request to Registry Server")
    except Exception as e:
        print(" [x] Error: %r" % e)


def handle_JoinServer(body):
    print(" [x] JOIN REQUEST FROM %r" % body["id"])
    message = {
        "from": "server",
        "id": unique_id,
        "address": address,
        "function": "JoinServer",
        "type": "reply",
    }
    if len(CLIENTELE) < config["max_clients_per_server"]:
        if body["id"] in CLIENTELE:
            print(
                " [x] Client Registration Failed %r. Reason: Client already registered"
                % body["id"]
            )
            message["message"] = "failed"
            message["reason"] = "already registered"

        else:
            CLIENTELE.add(body["id"])
            if body["from"] == "server":
                CLIENTELE_servers.add(body["id"])

            print(" [x] Client Registered %r" % body["id"])
            print(" [x] Clientele: %r" % CLIENTELE)
            print(
                " [x] Load: %r/%r" % (len(CLIENTELE), config["max_clients_per_server"])
            )
            message["message"] = "success"
    else:
        print(" [x] Client Registration Failed %r" % body["id"])
        message["message"] = "failed"
        message["reason"] = "server full"

    channel.basic_publish(exchange="", routing_key=body["id"], body=json.dumps(message))
    if message["message"] == "success" and body["from"] == "server":
        # TDOD: send all articles to new server
        print("sending all articles to new server")
        for article_key in ARTICLES:
            article = ARTICLES[article_key]
            message = {
                "from": "server",
                "id": unique_id,
                "address": address,
                "function": "PublishArticle",
                "type": "request",
                "article": {
                    "type": article.type,
                    "author": article.author,
                    "datetime": str(article.datetime),
                    "content": article.content,
                },
            }
            channel.basic_publish(
                exchange="", routing_key=body["id"], body=json.dumps(message)
            )


def handle_LeaveServer(body):
    global CLIENTELE
    print(" [x] LEAVE REQUEST FROM %r" % body["id"])
    CLIENTELE.remove(body["id"])
    print(" [x] Clientele: %r" % CLIENTELE)
    message = {
        "from": "server",
        "id": unique_id,
        "address": address,
        "function": "LeaveServer",
        "message": "success",
        "type": "reply",
    }
    channel.basic_publish(exchange="", routing_key=body["id"], body=json.dumps(message))


def handle_GetArticles(body):
    print(" [x] ARTICLES REQUEST FROM %r" % body["id"])

    articles_list = []
    requested_date = datetime.strptime(
        body["article"]["datetime"], "%Y-%m-%d %H:%M:%S.%f"
    )
    for article_key in ARTICLES:
        article = ARTICLES[article_key]
        if article.datetime >= requested_date:
            if (
                len(body["article"]["author"]) == 0
                or article.author == body["article"]["author"]
            ) and (
                len(body["article"]["type"]) == 0
                or article.type == body["article"]["type"]
            ):
                articles_list.append(
                    {
                        "type": article.type,
                        "author": article.author,
                        "date": str(article.datetime),
                        "content": article.content,
                    }
                )
    message = {
        "from": "server",
        "id": unique_id,
        "address": address,
        "function": "GetArticles",
        "message": articles_list,
        "type": "reply",
    }
    channel.basic_publish(exchange="", routing_key=body["id"], body=json.dumps(message))
    print(" [x] Articles Sent to %r" % body["id"])


def handle_PublishArticle(body):
    global CLIENTELE, ARTICLES
    print(" [x] ARTICLES PUBLISH FROM %r %r" % (body["id"], body["from"]))
    if body["id"] in CLIENTELE or body["id"] in JOINED_SERVERS:
        if body["from"] == "server":
            article = Article(
                body["article"]["type"],
                body["article"]["author"],
                body["article"]["content"][:200],
                datetime.strptime(body["article"]["datetime"], "%Y-%m-%d %H:%M:%S.%f"),
            )
        else:
            article = Article(
                body["article"]["type"],
                body["article"]["author"],
                body["article"]["content"][:200],
            )

        if generate_article_hash(article) not in ARTICLES:
            ARTICLES[generate_article_hash(article)] = article

            if body["from"] == "client":
                # Ack to Client
                message = {
                    "from": "server",
                    "id": unique_id,
                    "address": address,
                    "function": "PublishArticle",
                    "message": "success",
                    "type": "reply",
                }
                channel.basic_publish(
                    exchange="", routing_key=body["id"], body=json.dumps(message)
                )

            # Publish to client servers
            message = {
                "from": "server",
                "id": unique_id,
                "function": "PublishArticle",
                "article": {
                    "type": article.type,
                    "author": article.author,
                    "content": article.content,
                    "datetime": str(article.datetime),
                },
            }

            for server_that_is_client in CLIENTELE_servers:
                if server_that_is_client != body["id"]:
                    channel.basic_publish(
                        exchange="",
                        routing_key=server_that_is_client,
                        body=json.dumps(message),
                    )
        else:
            print("Article already exists")
    else:
        print(" [x] Article Publish Failed by %r" % body["id"])
        message = {
            "from": "server",
            "id": unique_id,
            "address": address,
            "function": "PublishArticle",
            "message": "failed",
            "type": "reply",
            "reason": "not registered",
        }

        channel.basic_publish(
            exchange="", routing_key=body["id"], body=json.dumps(message)
        )


def server_functionality():
    def callback_client(ch, method, properties, body):
        try:
            body = json.loads(body.decode())
        except Exception as e:
            print("Error:", e)
        print()
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
                print(" [x] Invalid request from", body["id"], ". Request:", body)

        elif body["from"] == "regserver":
            if body["function"] == "Register":
                if body["message"] == "success":
                    print(" [x] [SUCCESS] Server Registered Successfully")
                else:
                    print(" [x] [FAIL] Registration Failed on RegServer")
                    print("Exiting...")
                    exit(0)
            elif body["function"] == "GetServerList":
                global AVAILABLE_SERVERS
                AVAILABLE_SERVERS = []
                # uuid#address,uuid#address
                servers = body["message"].split(",")
                print(" [x] Server List:")
                i = 0
                for server in servers:
                    s = server.split("#")
                    if s[0] != unique_id:
                        AVAILABLE_SERVERS.append(s[0])
                        print("Server %r.   %r    %r" % (i, s[0], s[1]))
                        i += 1
                print()
        elif body["from"] == "server":
            if body["function"] == "JoinServer":
                if body["type"] == "request":
                    handle_JoinServer(body)
                else:
                    if body["message"] == "success":
                        print(" [x] Successfully joined server %r" % body["id"])
                        JOINED_SERVERS.add(body["id"])
                    else:
                        print(" [x] Failed to join server. Reason:", body["reason"])

            elif body["function"] == "LeaveServer":
                if body["type"] == "request":
                    handle_LeaveServer(body)
                else:
                    if body["message"] == "success":
                        print(" [x] Successfully left server %r" % body["id"])
                        JOINED_SERVERS.remove(body["id"])
                    else:
                        print(" [x] Failed to leave server.")
            elif body["function"] == "PublishArticle":
                handle_PublishArticle(body)
            else:
                print(" [x] Invalid request from", body["id"], ". Request:", body)

    channel.basic_consume(
        queue=unique_id, on_message_callback=callback_client, auto_ack=True
    )
    channel.start_consuming()


def communicate_with_other_servers():
    while True:
        sleep(1)
        method_number, function = util.select_one_from_list(
            ["GetServerList", "JoinServer", "LeaveServer"], "Enter the method number"
        )

        # Exit
        if method_number == -1:
            util.quit()

        # GetServerList | RegServer
        elif method_number == 0:
            message = {
                "from": "server",
                "id": unique_id,
                "address": address,
                "function": "GetServerList",
                "type": "request",
            }
            channel.basic_publish(
                exchange="", routing_key="regserver", body=json.dumps(message)
            )
            print(" [x] GetServerList Request Sent")

        # JoinServer or LeaveServer
        elif method_number == 1 or method_number == 2:
            if len(AVAILABLE_SERVERS) == 0:
                print(
                    "No servers available to join. Refresh the list by using `GetServerList`."
                )
                continue

            print("Here is the list of available servers:")
            server_num, server_id = util.select_one_from_list(
                AVAILABLE_SERVERS if method_number == 1 else JOINED_SERVERS,
                "Enter the server number that you would like to join",
            )
            if server_num == -1:
                continue

            message = {
                "from": "server",
                "id": unique_id,
                "address": address,
                "function": function,
                "type": "request",
            }
            channel.basic_publish(
                exchange="", routing_key=server_id, body=json.dumps(message)
            )

        else:
            print("Invalid method number")


def main():
    util.print_status("Server", unique_id, PORT)
    channel.queue_declare(queue=unique_id)
    register()

    # Create a thread to handle publishing messages
    publishing_thread = threading.Thread(
        target=lambda: communicate_with_other_servers()
    )

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
        util.print_node_type("server")
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        util.quit()
