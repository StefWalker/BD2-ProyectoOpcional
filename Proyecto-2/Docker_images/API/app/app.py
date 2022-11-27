import datetime
import os
import re
import mariadb
import prometheus_client
from prometheus_client import Counter
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from flask import Flask, jsonify, request, Response
from flask_ngrok import run_with_ngrok
from flask_cors import CORS
from elasticsearch import Elasticsearch
from requests.exceptions import *

# Metricas personalizadas
metrics = {}
metrics['requests'] = Counter('total_requests', 'The total number of processed requests')
metrics['error'] = Counter('total_request_error', 'The Total number of error requests')
metrics['docs'] = Counter('total_docs', 'The Total number of documents searched')

# Instancia de la aplicación con flask, ngrok y cors
app = Flask(__name__)
run_with_ngrok(app)
CORS(app)

# Se obtienen ingresan las credenciales de FireBase para usar la base de datos personal
cred = credentials.Certificate('adminSecret.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://tareacorta2-2f12e-default-rtdb.firebaseio.com/'
})

# Variables de entorno
ELASTICURL = os.getenv('ELASTICURL')
ELASTICPASS = os.getenv('ELASTICPASS')
ESINDEXGROUPS = os.getenv('ESINDEXGROUPS')

# Conexion a Elasticsearch
client = Elasticsearch("https://" + ELASTICURL + ":9200", basic_auth = ("elastic", ELASTICPASS), verify_certs = False)

# Limpia los datos del indice
def resetIndex():
    if client.indices.exists(index = ESINDEXGROUPS):
        client.indices.delete(index = ESINDEXGROUPS)
        print("Indice groups eliminado")
    client.indices.create(index = ESINDEXGROUPS)
    print("Indice groups creado")

# Request básico para buscar los primeros 10 artículos
@app.route('/elastic', methods=["POST"])
def search():
    word = request.json["data"]
    result = client.search(index = ESINDEXGROUPS, body = {"query":{"match_all":{}}})["hits"]["hits"]
    docs = []
    limit = 10
    count = 0
    for search in result:
        if count == limit:
            break
        doc = search["_source"]["docs"]
        for article in doc:
            if count == limit:
                break
            collection = article["collection"]
            for data in collection:
                if count == limit:
                    break
                if re.search(word.lower(), data["rel_title"].lower()) != None:
                    docs.append(data)
                    count += 1
                    print("Articulo agregado: " + data["rel_title"])
    metrics['requests'].inc()
    metrics['docs'].inc(count)
    return jsonify(docs)

# Request para buscar otros 10 artículos relacionados
@app.route('/elasticMore', methods=["POST"])
def searchMore():
    word = request.json["data"]
    last = request.json["offset"]
    result = client.search(index = ESINDEXGROUPS, body = {"query":{"match_all":{}}})["hits"]["hits"]
    docs = []
    limit = 10
    count = 0
    insertFlag = False
    for search in result:
        if count == limit:
            break
        doc = search["_source"]["docs"]
        for article in doc:
            if count == limit:
                break
            collection = article["collection"]
            for data in collection:
                if count == limit:
                    break
                if re.search(word.lower(), data["rel_title"].lower()) != None and insertFlag:
                    docs.append(data)
                    count += 1
                    print("Articulo agregado: " + data["rel_title"])
                if data["rel_title"] == last:
                    insertFlag = True
    metrics['requests'].inc()
    metrics['docs'].inc(count)
    return jsonify(docs)

# Request para añadir un artículo con like del usuario a Firebase
@app.route('/addLike/<data>', methods=["POST"])
def addLike(data):
    try:
        # Global JSON path
        ref = db.reference('/Users/' + str(data))
        # Get all the data from the reference
        user = ref.get()
        try:
            # Actualiza la lista de artículos
            ref.update({
                'articles': user["articles"] + [{"title": request.json['title'], "auth":request.json['auth'], "abs":request.json['abs']}]
            })
        except:
            # Crea una lista de artículos si no existe
            ref.update({
                'articles': [{"title": request.json['title'], "auth":request.json['auth'], "abs":request.json['abs']}]
            })
        metrics['requests'].inc()
        return jsonify(ref.get())
    except RequestException as e:
        metrics['error'].inc()
        return jsonify("Error: " + str(e))
    

# Request para agregar un job a MariaDB
@app.route('/addGrp/<data>', methods=["POST"])
def addGrp(data):
    # Variables de entorno
    IP = os.getenv('POD_IP')
    HOSTMARIA = os.getenv('MARIADB')
    MARIAPASS = os.getenv('MARIAPASS')

    # Conexion al servicio de la base de datos Mariadb
    mariaDatabase = mariadb.connect(
        host=HOSTMARIA,
        port=3306,
        user="user", 
        password=MARIAPASS,
        database="my_database"
    )
    connection = mariaDatabase.cursor()
    # Crear request para insertar el grupo
    connection.execute("INSERT INTO jobs(created,end,status,loader,grp_size) \
                      VALUES (?,?,?,?,?)",(datetime.datetime.now(), datetime.datetime.now(), 'In progress', str(IP), int(data)))
    mariaDatabase.commit()
    mariaDatabase.close()
    metrics['requests'].inc()
    return jsonify(data)

@app.route('/', methods=["GET"])
def init():
    metrics['requests'].inc()
    return jsonify("Journal Search Platform (JSP)'s API")

@app.route('/metrics')
def requests_count():
    results = []
    # Muestra las metricas personalizadas
    for k,v in metrics.items():
        results.append(prometheus_client.generate_latest(v))
    return Response(results, mimetype="text/plain")

app.run()