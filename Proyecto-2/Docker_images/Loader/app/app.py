import time
import os
import sys
import requests
'''
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
'''

response = requests.get("https://api.biorxiv.org/covid19/0").json()
#print(response["collection"][0])



import mysql.connector
# pip install mariadb
# pip install mysql-connector-python
mysqlDatabase = mysql.connector.connect(
  host="127.0.0.1",
  port="60800",
  user="user", 
  password="user",
  database="my_database",
  charset="utf8mb3"
)

connection = mysqlDatabase.cursor()

connection.execute("CREATE TABLE customers (name VARCHAR(255), address VARCHAR(255))")

#connection.execute("SHOW TABLES")

#for x in connection:
#  print(x)