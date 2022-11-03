import time
import os
import sys
import pika
from datetime import datetime
from elasticsearch import Elasticsearch
import hashlib
import json

def callback(ch, method, properties, body):
    json_object = json.loads(body)
    resp = client.index(index = ESINDEX, id = hashlib.md5(body).hexdigest(), document = json_object)
    print(resp)
    print(" [x] Received %r" % body)

DATA = os.getenv('DATAFROMK8S')
RABBIT_MQ = os.getenv('RABBITMQ')
RABBIT_MQ_PASSWORD = os.getenv('RABBITPASS')
QUEUE_NAME = os.getenv('RABBITQUEUE')
ESENDPOINT = os.getenv('ESENDPOINT')
ESPASSWORD = os.getenv('ESPASSWORD')
ESINDEX = os.getenv('ESINDEX')

client = Elasticsearch("https://" + ESENDPOINT + ":9200", basic_auth = ("elastic", ESPASSWORD), verify_certs = False)

credentials = pika.PlainCredentials('user', RABBIT_MQ_PASSWORD)
parameters = pika.ConnectionParameters(host = RABBIT_MQ, credentials = credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue = QUEUE_NAME)
channel.basic_consume(queue = QUEUE_NAME, on_message_callback = callback, auto_ack = True)
print(' [*] Waiting for messages. TO exit press CTRL+C')
channel.start_consuming()