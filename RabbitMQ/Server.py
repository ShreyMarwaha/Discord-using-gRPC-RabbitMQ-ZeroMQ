import uuid
import pika
import sys
import os
import util
import json
import uuid
from datetime import date, datetime

config = json.load(open('config.json'))
channel = util.connect(config['host'], config['port'])
unique_id = str(uuid.uuid1())
CLIENTELE = []
ARTICLES = []


class article:
    # class to store article, contains type, author, time, content
    def __init__(self, type, author, content):
        self.type = type
        self.author = author
        self.time = date.today()
        self.content = content


def register():
    message = {"from": 'server', "id": unique_id, "function": "Register"}
    channel.basic_publish(
        exchange='', routing_key='regserver', body=str(message))
    print(" [x] Sent Register request to Registry Server")


def handle_JoinServer(body):
    if len(CLIENTELE) < config.max_clients_per_server:
        CLIENTELE.append(body['id'])
        print(" [x] Client Registered %r" % body['id'])
        print(" [x] Clientele: %r" % CLIENTELE)
        message = {"from": 'server', "id": unique_id, "function": "JoinServer",
                   "message": "success"}
        channel.basic_publish(
            exchange='', routing_key=body[id], body=str(message))
    else:
        print(" [x] Client Registration Failed %r" % body['id'])
        message = {"from": 'server', "id": unique_id,
                   "function": "JoinServer", "message": "failed"}
        channel.basic_publish(
            exchange='', routing_key=body[id], body=str(message))


def handle_LeaveServer(body):
    global CLIENTELE
    print(" [x] Leave request from %r" % body['id'])
    CLIENTELE.remove(body['id'])
    print(" [x] Clientele: %r" % CLIENTELE)
    message = {"from": 'server', "id": unique_id, "function": "LeaveServer",
               "message": "success"}
    channel.basic_publish(
        exchange='', routing_key=body[id], body=str(message))


def handle_GetArticles(body):
    print(" [x] GetArticles request from %r" % body['id'])
    articles_list = {}
    requested_date = datetime.strptime(
        body["article"]["date"], "%Y-%m-%d").date()
    for i, article in enumerate(ARTICLES):
        if article.date >= requested_date:
            if (body["article"]["author"] is None or article.author == body["article"]["author"]) and (body["article"]["type"] is None or article.type == body["article"]["type"]):
                articles_list[i] = article
    message = {"from": 'server', "id": unique_id,
               "function": "GetArticles", "message": articles_list}
    channel.basic_publish(
        exchange='', routing_key=body[id], body=str(message))
    print(" [x] Articles Sent to %r" % body['id'])


def handle_PublishArticle(body):
    global CLIENTELE, ARTICLES
    print(" [x] PublishArticle request from %r" % body['id'])
    if body["id"] in CLIENTELE:
        ARTICLES.append(
            article(body["article"]["type"], body["article"]["author"], body["article"]["content"][:200]))
        print(" [x] Article Published by%r" % body['id'])

        message = {"from": 'server', "id": unique_id, "function": "PublishArticle",
                   "message": "success"}
        channel.basic_publish(
            exchange='', routing_key=body[id], body=str(message))
    else:
        print(" [x] Article Publish Failed by %r" % body['id'])
        message = {"from": 'server', "id": unique_id,
                   "function": "PublishArticle", "message": "failed"}
        channel.basic_publish(
            exchange='', routing_key=body[id], body=str(message))


def main():
    print(' [*] Name: Server,  Status: Online. \nTo exit press CTRL+C')
    channel.queue_declare(queue=unique_id)
    register()

    def callback_client(ch, method, properties, body):
        body = json.loads(body.decode())

        if body['from'] == 'client':
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
                      body['id'], ". Request:", body)

        elif body['from'] == 'regserver':
            if body['message'] == 'success':
                print(" [x] Server Registered Successfully")
            else:
                print(" [x] Registration Failed on RegServer")
                print("Exiting...")
                exit(0)

    channel.basic_consume(
        queue=unique_id, on_message_callback=callback_client, auto_ack=True)
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
