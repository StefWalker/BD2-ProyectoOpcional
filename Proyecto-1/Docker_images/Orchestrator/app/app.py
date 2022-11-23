import time
import os
import sys
import pika
from elasticsearch import Elasticsearch
import json
import mariadb
from mariadb import Error
import math

# Variables de entorno
RABBIT_MQ = os.getenv('RABBITMQ')
RABBIT_MQ_PASSWORD = os.getenv('RABBITPASS')
EXTRACT_QUEUE = os.getenv('EXTRACTQUEUE')
ESENDPOINT = os.getenv('ESENDPOINT')
ESPASSWORD = os.getenv('ESPASSWORD')
ESINDEXJOBS = os.getenv('ESINDEXJOBS')
ESINDEXGROUPS = os.getenv('ESINDEXGROUPS')
MARIA = os.getenv('MARIADB')

# Conexion a Elasticsearch
client = Elasticsearch("https://" + ESENDPOINT + ":9200", basic_auth = ("elastic", ESPASSWORD), verify_certs = False)

# Conexion a RabbitMQ
credentials = pika.PlainCredentials('user', RABBIT_MQ_PASSWORD)
parameters = pika.ConnectionParameters(host = RABBIT_MQ, credentials = credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue = EXTRACT_QUEUE)

# Devuelve un json de la lista dada
def findJSON(key, value, lista):
    for x in lista:
        if x[key] == value:
            return x
    return None


while True:
    # busca nuevos jobs
    resp = client.search(index=ESINDEXJOBS, body={"query":{"match":{"status" : "new"}}})
    for hit in resp["hits"]["hits"]:
        job = hit["_source"]
        print("job en proceso:")
        print(job)
        job["status"] = "In-Progress"
        client.index(index = ESINDEXJOBS, id = hit["_id"], document = job)
        data_source = findJSON("name", job["source"]["data_source"], job["data_sources"])
        if data_source is not None:
            try:
                # Conexion a la base de datos
                connection = mariadb.connect(host=MARIA, port=3306,user="user",password="user",database="my_database")
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(1) FROM (" + job["source"]["expression"] + ") as Personas")
                total_registros = 0
                # Obtiene resultado del query
                for result in cursor:
                    total_registros = result[0]
                cant_grupos = math.ceil(total_registros/int(job["source"]["grp_size"]))
                # Publica documentos a Elasticsearch y RabbitMQ
                while cant_grupos > 0:
                    doc = {"job_id" : job["job_id"], "group_id" : job["job_id"] + "-" + str(cant_grupos)}
                    put_res = client.index(index = ESINDEXGROUPS, id = doc["group_id"], document = doc)
                    channel.basic_publish(exchange = '', routing_key = EXTRACT_QUEUE, body = json.dumps(doc))
                    print("documento publicado:")
                    print(doc)
                    print(put_res)
                    cant_grupos = cant_grupos - 1
            except Error as e:
                print("Error en la conexion a la base de datos: ", e)
        else:
            print("No se encontro el data source " + job["source"]["data_source"])
    time.sleep(1)

connection.close()
