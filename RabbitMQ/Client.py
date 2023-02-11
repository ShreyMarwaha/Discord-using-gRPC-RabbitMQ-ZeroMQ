import threading
import pika
import json
import util
import uuid

config = json.load(open('config.json'))
channel = util.connect(config['host'], config['port'])
unique_id = str(uuid.uuid1())
SERVERS = []


def getServerList():
    message = {"from": 'server', "id": unique_id}
    channel.basic_publish(
        exchange='', routing_key='regserver', body=str(message))
    for server in SERVERS:
        message += server + ','
    return message


def publish_message(method_number):
    functions = ["GetServerList", "JoinServer",
                 "LeaveServer", "GetArticles", "PostArticle"]
    message = {"from": "client", "id": unique_id,
               "function": functions[method_number]}
    # GetServerList
    if method_number == 0:
        channel.basic_publish(
            exchange='', routing_key='regserver', body=str(message))
        print(" [x] Requested Server List...")

    elif 1 <= method_number <= 4:
        print("Here is the list of servers.")
        for i in range(len(SERVERS)):
            print(str(i) + ". " + SERVERS[i])
        server_num = int(
            input("Enter the server number that you would like to message:"))
        channel.basic_publish(
            exchange='', routing_key=SERVERS[server_num], body=str(message))
        print(" [x] Requested " + functions[method_number] +
              " from " + SERVERS[server_num] + "...")


def handle_server_response(body):
    if body["function"] == "JoinServer":
        if body["message"] == "success":
            print(" [x] Successfully joined server %r" % body["id"])
        else:
            print(" [x] Failed to join server.")

    elif body["function"] == "LeaveServer":
        if body["message"] == "success":
            print(" [x] Successfully left server %r" % body["id"])
        else:
            print(" [x] Failed to leave server.")

    elif body["function"] == "GetArticles":
        print(" [x] Articles from server %r" % body["id"])
        print(body["message"])
    elif body["function"] == "PostArticle":
        if body["message"] == "success":
            print(" [x] Successfully posted article to server %r" % body["id"])
        else:
            print(" [x] Failed to post article to server.")
    else:
        print(" [x] Unrecognized Response from %r" % body["id"])


def consume_messages():
    for method_frame, properties, body in channel.consume(unique_id):
        body = json.loads(body.decode())
        if body['from'] == 'server':
            handle_server_response(body)
        elif body['from'] == 'regserver':
            global SERVERS
            SERVERS = body['message'].split(',')
            print(" [x] Server List: %r" % SERVERS)
        else:
            print(" [x] Unrecognized Request from %r" % body['id'])
        channel.basic_ack(method_frame.delivery_tag)
    channel.cancel()


def main():
    channel.queue_declare(queue=unique_id)

    # Create a thread to handle publishing messages
    publishing_thread = threading.Thread(
        target=lambda: publish_message(input("""
        Enter a method number:
        1. GetServerList
        2. JoinServer
        3. LeaveServer
        4. GetArticles
        5. PostArticle""")))

    # Create a thread to handle consuming messages
    consuming_thread = threading.Thread(target=consume_messages)
    # Start both threads
    consuming_thread.start()
    publishing_thread.start()

    # Wait for both threads to finish
    consuming_thread.join()
    publishing_thread.join()

    connection.close()


"""
Send
1. GetServerList
2. JoinServer
3. LeaveServer
4. GetArticles
5. PostArticle
"""


# Connection parameters
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='queue_name')

# Function to publish messages to the queue


# Close the connection
