import time
import os
import sys
import pika
from datetime import datetime
from elasticsearch import Elasticsearch
import hashlib
import json
import mariadb
from mariadb import Error

# Devuelve un json de la lista dada
def findJSON(key, value, lista):
    for x in lista:
        if x[key] == value:
            return x
    return None

# Reemplaza el destination_queue del stage extract
def replace_value(client, indice, doc_id, job):
    for stage in job["stages"]:
        if stage["name"] == "extract" and stage["destination_queue"][:2] == "%{" and stage["destination_queue"][-2:] == "}%":
            path = stage["destination_queue"][2:-2].split("->")
            destination = job["stages"]
            for dest in destination:
                if dest["name"] == path[0]:
                    for transformation in dest[path[1]]:
                        if transformation["name"] == path[2]:
                            stage["destination_queue"] = transformation["source_queue"]
                            client.index(index = indice, id = doc_id, document = job)
                            break
                    break
            break


def callback(ch, method, properties, body):
    doc = json.loads(body)
    print("documento recibido:")
    print(doc)
    doc_id = ""
    job = None
    resp = client.search(index=ESINDEXJOBS, body={"query":{"match":{"status" : "In-Progress"}}})
    for hit in resp["hits"]["hits"]:
        if hit["_source"]["job_id"] == doc["job_id"]:
            # Reemplaza valor
            doc_id = hit["_id"]
            job = hit["_source"]
            replace_value(client, ESINDEXJOBS, doc_id, job)
            print("job recibido:")
            print(job)
            print("Id del documento:")
            print(doc_id)
            break
    data_source = findJSON("name", job["source"]["data_source"], job["data_sources"])
    if data_source is not None:
        try:
            # Conexion a la base de datos
            connection = mariadb.connect(host='127.0.0.1', port=3305, database="my_database", user=data_source["usuario"], password=data_source["password"])
            cursor = connection.cursor()
            cursor.execute(job["source"]["expression"] + " LIMIT " + doc["group_id"].split("-")[1] + ", " + job["source"]["grp_size"])
            # Saca el query como una lista de json
            headers = [x[0] for x in cursor.description]
            rv = cursor.fetchall()
            data = []
            for result in rv:
                data.append(dict(zip(headers, result)))
            # Actualiza el grupo
            doc["docs"] = data
            update_res = client.index(index = ESINDEXGROUPS, id = doc["group_id"], document = doc)
            print("documento actualizado:")
            print(doc)
            # Publica el documento a la siguiente cola
            del doc["docs"]
            channel.basic_publish(exchange = '', routing_key = SQL_QUEUE, body = json.dumps(doc))
            print("documento publicado:")
            print(doc)
            print(update_res)
        except Error as e:
            print("Error en la conexion a la base de datos: ", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        print("No se encontro el data source " + job["source"]["data_source"])


# Variables de entorno
RABBIT_MQ = os.getenv('RABBITMQ')
RABBIT_MQ_PASSWORD = os.getenv('RABBITPASS')
EXTRACT_QUEUE = os.getenv('EXTRACTQUEUE')
SQL_QUEUE = os.getenv('SQL_QUEUE')
ESENDPOINT = os.getenv('ESENDPOINT')
ESPASSWORD = os.getenv('ESPASSWORD')
ESINDEXJOBS = os.getenv('ESINDEXJOBS')
ESINDEXGROUPS = os.getenv('ESINDEXGROUPS')

# Conexion a Elasticsearch
client = Elasticsearch("https://" + ESENDPOINT + ":9200", basic_auth = ("elastic", ESPASSWORD), verify_certs = False)

# Conexion a RabbitMQ
credentials = pika.PlainCredentials('user', RABBIT_MQ_PASSWORD)
parameters = pika.ConnectionParameters(host = RABBIT_MQ, credentials = credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue = EXTRACT_QUEUE)
channel.queue_declare(queue = SQL_QUEUE)
channel.basic_consume(queue = EXTRACT_QUEUE, on_message_callback = callback, auto_ack = True)
print("Esperando mensaje")
channel.start_consuming()