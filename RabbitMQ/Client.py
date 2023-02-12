import threading
import pika
import json
import os
import sys
import uuid
from time import sleep

config = json.load(open("config.json"))
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue="regserver")
unique_id = str(uuid.uuid1())
AVAILABLE_SERVERS = []
JOINED_SERVERS = []


def ask(what_to_ask):
    _ = ""
    while len(_) == 0:
        _ = input(what_to_ask)
    return _


def quit():
    print("Exiting...")
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)


def select_one_from_list(arr, msg):
    print("\n\n"+msg+" (Exit with -1)")
    for i, ele in enumerate(arr):
        print(str(i) + ". " + ele)

    select = int(input("Select: "))
    while select < -1 or len(arr) <= select:
        print(select)
        print(" [x] Invalid Selection. Select in the range [-1, %r]" %
              (len(arr)-1))
        select = int(input("Select: "))

    if select >= 0:
        return select, arr[select]
    return -1, ""


def publish_message():
    while True:
        try:
            method_number, function = select_one_from_list(
                ["GetServerList", "JoinServer", "LeaveServer", "GetArticles", "PublishArticle"], "Enter the method number")
            if method_number == -1:
                quit()

            # GetServerList
            if method_number == 0:
                message = {"from": "client",
                           "id": unique_id, "function": function}
                channel.basic_publish(
                    exchange="", routing_key="regserver", body=json.dumps(message))
                print(" [x] Requested Server List...")
                sleep(1)

            elif 1 <= method_number <= 4:
                if method_number == 1 and len(AVAILABLE_SERVERS) == 0:
                    print(
                        "No servers available to join. Refresh the list by using `GetServerList`.")
                    continue
                elif method_number > 1 and len(JOINED_SERVERS) == 0:
                    print("You must join a server before you can communicate with it.")
                    continue

                print("Here is the list of servers.")
                servers = AVAILABLE_SERVERS if method_number == 1 else JOINED_SERVERS
                server_num, server_id = select_one_from_list(
                    servers, "Enter the server number that you would like to message")

                if server_num == -1:
                    continue
                message = {"from": "client", "id": unique_id,
                           "function": function}
                if method_number == 4:
                    message = {"from": "client", "id": unique_id,
                               "function": function, "article": None}
                    _, type = select_one_from_list(
                        ["SPORTS", "FASHION", "POLITICS"], "Article Type")
                    if _ == -1:
                        continue
                    author = ask("Article Author: ")
                    content = ask("Article Content (max 200 char): ")[:200]
                    article = {"type": type,
                               "author": author, "content": content}
                    message["article"] = article
                elif method_number == 3:
                    message = {"from": "client", "id": unique_id,
                               "function": function, "article": None}

                    type = input("Article Type (Optional): ")
                    if len(type) > 0:
                        while len(type) > 0 and type not in ["SPORTS", "FASHION", "POLITICS"]:
                            print(
                                " [x] Invalid Article Type. Select from SPORTS, FASHION, POLITICS or leave blank.")
                            type = input("Article Type (Optional): ")

                    author = input("Article Author (Optional): ")
                    date = ask("Date (as YYYY-MM-DD): ")
                    article = {"type": type,
                               "author": author, "date": date}
                    message["article"] = article

                channel.basic_publish(
                    exchange="", routing_key=server_id, body=json.dumps(message))
                print(" [x] Requested " + function +
                      " from " + server_id + "...")
                sleep(1)
            else:
                print("[x] Invalid method number.")

        except:
            print("Exiting...")


def handle_server_response(body):
    if body["function"] == "JoinServer":
        if body["message"] == "success":
            print(" [x] Successfully joined server %r" % body["id"])
            JOINED_SERVERS.append(body["id"])
        else:
            print(" [x] Failed to join server. Reason:", body["reason"])

    elif body["function"] == "LeaveServer":
        if body["message"] == "success":
            print(" [x] Successfully left server %r" % body["id"])
        else:
            print(" [x] Failed to leave server.")

    elif body["function"] == "GetArticles":
        print(" [x] Articles from server %r" % body["id"])
        articles = body["message"]
        for article in articles:
            print(article["date"])
            print(article["topic"])
            print(article["author"])
            print(article["content"])
            print()
        print()
    elif body["function"] == "PublishArticle":
        if body["message"] == "success":
            print(" [x] Successfully posted article to server %r" % body["id"])
        else:
            print(" [x] Failed to post article to server.")
    else:
        print(" [x] Unrecognized Response from %r" % body["id"])


def consume_messages():
    for method_frame, properties, body in channel.consume(unique_id):
        body = json.loads(body.decode())
        if body["from"] == "server":
            handle_server_response(body)
        elif body["from"] == "regserver":
            global AVAILABLE_SERVERS
            AVAILABLE_SERVERS = body["message"].split(",")
            print(" [x] Server List: %r" % AVAILABLE_SERVERS)
        else:
            print(" [x] Unrecognized Request from %r" % body["id"])
        channel.basic_ack(method_frame.delivery_tag)
    channel.cancel()


def main():
    channel.queue_declare(queue=unique_id)

    # Create a thread to handle publishing messages
    publishing_thread = threading.Thread(target=lambda: publish_message())

    # Create a thread to handle consuming messages
    consuming_thread = threading.Thread(target=consume_messages)
    # Start both threads
    consuming_thread.start()
    publishing_thread.start()

    # Wait for both threads to finish
    consuming_thread.join()
    publishing_thread.join()

    connection.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        quit()

"""
Send
1. GetServerList
2. JoinServer
3. LeaveServer
4. GetArticles
5. PublishArticle
"""
