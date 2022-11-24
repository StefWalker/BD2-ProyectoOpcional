import time
import os
import sys
import pika
from datetime import datetime
from elasticsearch import Elasticsearch
import json
import mariadb
from mariadb import Error
import requests

def callback(ch, method, properties, body):
    # Recibe mensaje
    doc = json.loads(body)
    print("documento recibido:")
    print(doc)
    id_job = str(doc["id_job"])
    grp_number = str(doc["grp_number"])
    cursor.execute("UPDATE groups SET stage = \"downloader\", status = \"in-progress\" WHERE id_job = " + id_job + " AND grp_number = " + grp_number)
    # Obtiene el grupo
    maria.commit()
    cursor.execute("SELECT * FROM groups WHERE id_job = " + id_job + " AND grp_number = " + grp_number)
    query_result = cursor.fetchall()
    if query_result != []:
        group = query_result[0]
        print("Grupo encontrado en la base de datos")
        # Inserta history
        cursor.execute("INSERT INTO history(stage, status, created, end, message, grp_id, component) \
                        VALUES (\"downloader\", \"in-progress\", now(), null, null, " + str(group[0]) + ", \"" + POD_NAME + "\")")
        # Obtiene tamaño del grupo
        maria.commit()
        cursor.execute("SELECT grp_size FROM jobs WHERE id = " + id_job)
        query_result = cursor.fetchall()
        if query_result != []:
            grp_size = query_result[0][0]
            # Obtiene documentos
            print("Descargando documentos")
            documents = []
            for i in range(group[7], grp_size + group[7]):
                response = requests.get(BIORXIV + str(i)).json()
                if response["messages"][0]["status"] != "ok":
                    break
                documents.append(response)
                break
            # Publica el mensaje con los documentos al indice de Elasticsearch
            doc["docs"] = documents
            client.index(index = ESINDEXGROUPS, id = id_job + "-" + grp_number, document = doc)
            print("documento publicado en el indice groups")
            del doc["docs"]
            # Actualiza valores
            cursor.execute("UPDATE history SET status = \"completed\", end = now() WHERE grp_id = " + str(group[0]))
            maria.commit()
            cursor.execute("UPDATE groups SET status = \"completed\" WHERE id_job = " + id_job + " AND grp_number = " + grp_number)
            # Publica mensaje a la cola de salida
            maria.commit()
            channel.basic_publish(exchange = '', routing_key = OUTQUEUE, body = json.dumps(doc))
            print("documento enviado:")
            print(doc)
        else:
            print("Error en el downloader: no existe el job")
    else:
        print("Error en el downloader: no existe el job o el numero de grupo")
    print("-----------------------------------------------------------------")

# Variables de entorno
POD_NAME = os.getenv('POD_NAME')
BIORXIV = os.getenv('BIORXIV')
RABBIT_MQ = os.getenv('RABBITMQ')
RABBIT_MQ_PASSWORD = os.getenv('RABBITPASS')
MARIADB = os.getenv('MARIADB')
MARIADBPASS = os.getenv('MARIADBPASS')
INQUEUE = os.getenv('INQUEUE')
OUTQUEUE = os.getenv('OUTQUEUE')
ESENDPOINT = os.getenv('ESENDPOINT')
ESPASSWORD = os.getenv('ESPASSWORD')
ESINDEXGROUPS = os.getenv('ESINDEXGROUPS')

# Conexion a MariaDB
try:
    maria = mariadb.connect(host=MARIADB,
                            port=3306,
                            user="user", 
                            password=MARIADBPASS,
                            database="my_database")
    cursor = maria.cursor()
except Error as e:
    print("Error en la conexion a la base de datos: ", e)

# Conexion a Elasticsearch
client = Elasticsearch("https://" + ESENDPOINT + ":9200", basic_auth = ("elastic", ESPASSWORD), verify_certs = False)

# Conexion a RabbitMQ
credentials = pika.PlainCredentials('user', RABBIT_MQ_PASSWORD)
parameters = pika.ConnectionParameters(host = RABBIT_MQ, credentials = credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue = INQUEUE)
channel.queue_declare(queue = OUTQUEUE)
channel.basic_consume(queue = INQUEUE, on_message_callback = callback, auto_ack = True)
print('Esperando mensaje del loader')
channel.start_consuming()