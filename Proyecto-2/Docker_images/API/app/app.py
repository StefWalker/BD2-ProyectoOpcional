import datetime
import os
import re
import requests
import mariadb
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from flask import Flask, jsonify, request
from flask_ngrok import run_with_ngrok
from flask_cors import CORS

# Instancia de la aplicación con flask, ngrok y cors
app = Flask(__name__)
run_with_ngrok(app)
CORS(app)

# Se obtienen ingresan las credenciales de FireBase para usar la base de datos personal
cred = credentials.Certificate('adminSecret.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://tareacorta2-2f12e-default-rtdb.firebaseio.com/'
})

# Request básico para buscar los primeros 10 artículos
@app.route('/search', methods=["POST"])
def default():
    # Offset de la siguiente página de la última visitada
    apiPage = 0
    # Contador de artículos encontrados
    count = 0
    # Lista para guardar los artículos
    articles= []
    # Palabra a buscar en los títulos
    search = request.json["data"]
    while count < 10:
        # Se accede al API de Bio 
        response = requests.get("https://api.biorxiv.org/covid19/" + str(apiPage)).json()
        # Si el ciclo pasa del todal de artículos, se termina
        if apiPage == response["messages"][0]["total"]:
            break
        # Agrega el artículo encontrado y summa el contador
        if re.search(search.lower(), response["collection"][0]["rel_title"].lower()) != None:
            articles += [response["collection"][0]]
            count += 1
        # Cambio de página
        apiPage += 1
    response["collection"] = articles
    response["messages"][0]["total"] = apiPage
    return response

# Request para buscar otros 10 artículos relacionados
@app.route('/more', methods=["POST"])
def defaultMore():
    # Offset de la siguiente página de la última visitada
    apiPage = int(request.json["offset"])
    # Contador de artículos encontrados
    count = 0
    # Lista para guardar los artículos
    articles= []
    # Palabra a buscar en los títulos
    search = request.json["data"]
    while count < 10:
        # Se accede al API de Bio 
        response = requests.get("https://api.biorxiv.org/covid19/" + str(apiPage)).json()
        # Si el ciclo pasa del todal de artículos, se termina
        if apiPage == response["messages"][0]["total"]:
            break
        # Agrega el artículo encontrado y summa el contador
        if re.search(search.lower(), response["collection"][0]["rel_title"].lower()) != None:
            articles += [response["collection"][0]]
            count += 1
        # Cambio de página
        apiPage += 1
    response["collection"] = articles
    response["messages"][0]["total"] = apiPage
    return response

# Request para añadir un artículo con like del usuario a Firebase
@app.route('/addLike/<data>', methods=["POST"])
def addLike(data):
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
    return jsonify(ref.get())

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
    return jsonify(data)

@app.route('/', methods=["GET"])
def init():
    return jsonify("Journal Search Platform (JSP)'s API")

app.run()