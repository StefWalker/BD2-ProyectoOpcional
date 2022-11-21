import time
import os
import sys
import pika
from datetime import datetime
from elasticsearch import Elasticsearch
import hashlib
import json

def callback(ch, method, properties, body):
    '''json_object = json.loads(body)
    resp = client.index(index = ESINDEX, id = hashlib.md5(body).hexdigest(), document = json_object)
    print(resp)
    print(" [x] Received %r" % body)'''
    #resp = client.get(index="jobs", id=1)
    resp = client.search(index="jobs", body={"query":{"match":{"status" : "new"}}})
    print(resp)

RABBIT_MQ = os.getenv('RABBITMQ')
RABBIT_MQ_PASSWORD = os.getenv('RABBITPASS')
SQL_QUEUE = os.getenv('SQL_QUEUE')
REGEX_QUEUE = os.getenv('REGEX_QUEUE')
ESENDPOINT = os.getenv('ESENDPOINT')
ESPASSWORD = os.getenv('ESPASSWORD')
ESINDEXJOBS = os.getenv('ESINDEXJOBS')
ESINDEXGROUPS = os.getenv('ESINDEXGROUPS')

client = Elasticsearch("https://" + ESENDPOINT + ":9200", basic_auth = ("elastic", ESPASSWORD), verify_certs = False)

credentials = pika.PlainCredentials('user', RABBIT_MQ_PASSWORD)
parameters = pika.ConnectionParameters(host = RABBIT_MQ, credentials = credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue = SQL_QUEUE)
channel.basic_consume(queue = SQL_QUEUE, on_message_callback = callback, auto_ack = True)
print(' [*] Waiting for messages. TO exit press CTRL+C')
channel.start_consuming()