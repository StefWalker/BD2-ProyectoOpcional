import time
import os
import sys
import pika
from datetime import datetime
from elasticsearch import Elasticsearch
import hashlib
import json
#####################################   hace queue_delcare a los dos queues y en el callback hace basic_publish
# nombres de las colas se sacaban del json y no serian env var
# hacer funcion para los datos que hay que sustituir (hace split y replace depende del caso)
# elimina el %{}% -> string[2:-2],          s[2:-2].split("->"), con un for hace el reemplazo
# el client.search hay que sacar la parte de hits
# señalar en los app.py los que ocupan hacer los replace y verifica que sea un replace y no un dato (%{ }%)
# como crear cosas en mysql para las tablas
def callback(ch, method, properties, body):
    '''json_object = json.loads(body)
    resp = client.index(index = ESINDEX, id = hashlib.md5(body).hexdigest(), document = json_object)
    print(resp)
    print(" [x] Received %r" % body)'''
    #resp = client.get(index="jobs", id=1)
    #resp = client.search(index="jobs", body={"query":{"match":{"status" : "new"}}})
    #print(resp)
    doc = json.loads(body)
    print("documento recibido:")
    print(doc)

RABBIT_MQ = os.getenv('RABBITMQ')
RABBIT_MQ_PASSWORD = os.getenv('RABBITPASS')
READY_QUEUE = os.getenv('READYQUEUE')
ESENDPOINT = os.getenv('ESENDPOINT')
ESPASSWORD = os.getenv('ESPASSWORD')
ESINDEXJOBS = os.getenv('ESINDEXJOBS')
ESINDEXGROUPS = os.getenv('ESINDEXGROUPS')

client = Elasticsearch("https://" + ESENDPOINT + ":9200", basic_auth = ("elastic", ESPASSWORD), verify_certs = False)

credentials = pika.PlainCredentials('user', RABBIT_MQ_PASSWORD)
parameters = pika.ConnectionParameters(host = RABBIT_MQ, credentials = credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue = READY_QUEUE)
channel.basic_consume(queue = READY_QUEUE, on_message_callback = callback, auto_ack = True)
print(' [*] Waiting for messages. TO exit press CTRL+C')
channel.start_consuming()