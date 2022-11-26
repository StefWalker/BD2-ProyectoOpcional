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
from requests.exceptions import *

# Pasa el string a un json valido
def formatJSON(msg):
    jSON = ""
    put = True
    for i in range(1, len(msg)-1):
        if msg[i] == '{' or msg[i] == '}':
            continue
        elif msg[i] == ':':
            put = False
        elif msg[i] == ',':
            put = True
        if put and msg[i] != '"':
            jSON += msg[i]
        elif not put and msg[i] == '"':
            continue
        else:
            jSON += msg[i]
    return '{' + jSON + '}'

def callback(ch, method, properties, body):
    # Recibe mensaje
    body2 = formatJSON(body.decode('utf-8','strict'))
    doc = json.loads(body2)
    print("documento recibido:")
    print(body)
    print("documento en JSON:")
    print(doc)
    id_job = str(doc["id_job"])
    grp_number = str(doc["grp_number"])
    # Obtiene el grupo
    resp = client.get(index = ESINDEXGROUPS, id = id_job + "-" + grp_number)
    if resp["found"]:
        document = resp["_source"]
        print("Grupo encontrado en Elasticsearch")
        cursor.execute("UPDATE groups SET stage = \"details-downloader\", status = \"in-progress\" WHERE id_job = " + id_job + " AND grp_number = " + grp_number)
        maria.commit()
        cursor.execute("SELECT * FROM groups WHERE id_job = " + id_job + " AND grp_number = " + grp_number)
        query_result = cursor.fetchall()
        if query_result != []:
            group = query_result[0]
            print("Grupo encontrado en la base de datos")
            # Inserta history
            cursor.execute("INSERT INTO history(stage, status, created, end, message, grp_id, component) \
                            VALUES (\"details-downloader\", \"in-progress\", now(), null, null, " + str(group[0]) + ", \"" + POD_NAME + "\")")
            maria.commit()
            documents = document["docs"]
            # Agrega detalles a cada documento
            print("Agregando detalles")
            errorReq = False
            errorMsg = ""
            try:
                for bio in documents:
                    collection = bio["collection"]
                    for data in collection:
                        rel_doi = data["rel_doi"]
                        rel_site = data["rel_site"].lower()
                        details = requests.get(BIORXIV_DETAILS + rel_site + "/" + rel_doi).json()
                        data["details"] = details
                        print("Detalles obtenidos de rel_site: " + rel_site + " y rel_doi: " + rel_doi)
            except ConnectionError as e:
                errorReq = True
                errorMsg = "Error en la conexion: " + str(e)
                print(errorMsg)
            except Timeout as e:
                errorReq = True
                errorMsg = "Error limite de tiempo: " + str(e)
                print(errorMsg)
            except URLRequired as e:
                errorReq = True
                errorMsg = "Error en el link: " + str(e)
                print(errorMsg)
            except RequestException as e:
                errorReq = True
                errorMsg = "Error en el proceso: " + str(e)
                print(errorMsg)
            # Actualiza el grupo en el indice de Elasticsearch
            client.index(index = ESINDEXGROUPS, id = id_job + "-" + grp_number, document = document)
            print("documento actualizado en el indice groups")
            # Actualiza valores
            if errorReq:
                cursor.execute("UPDATE history SET status = \"error\", end = now(), message = " + errorMsg + " WHERE grp_id = " + str(group[0]))
            else:
                cursor.execute("UPDATE history SET status = \"completed\", end = now() WHERE grp_id = " + str(group[0]))
            maria.commit()
            cursor.execute("UPDATE groups SET status = \"completed\" WHERE id_job = " + id_job + " AND grp_number = " + grp_number)
            # Publica mensaje a la cola de salida
            maria.commit()
            channel.basic_publish(exchange = '', routing_key = OUTQUEUE, body = body)
            print("documento enviado:")
            print(body)
        else:
            print("Error en el details downloader: no existe el job o el numero de grupo")
    else:
        print("Error en el details downloader: no existe el documento en Elasticsearch")
    print("-----------------------------------------------------------------")

# Variables de entorno
POD_NAME = os.getenv('POD_NAME')
BIORXIV_DETAILS = os.getenv('BIORXIV_DETAILS')
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
parameters = pika.ConnectionParameters(host = RABBIT_MQ, credentials = credentials, heartbeat = 600)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue = INQUEUE)
channel.queue_declare(queue = OUTQUEUE)
channel.basic_consume(queue = INQUEUE, on_message_callback = callback, auto_ack = True)
print('Esperando mensaje del downloader')
channel.start_consuming()