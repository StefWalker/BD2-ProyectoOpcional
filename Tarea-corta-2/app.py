from flask import Flask, jsonify, request
from flask_ngrok import run_with_ngrok
from flask_cors import CORS
from data import markers
from data import users
from data import community

app = Flask(__name__)
CORS(app)

run_with_ngrok(app)
    
####
# Main get request for each element in the json 
# 

@app.route('/', methods=["GET"])
def getData():
    return jsonify({"data": markers})

@app.route('/markers', methods=["GET"])
def getData():
    return jsonify({"data": markers})

@app.route('/users', methods=["GET"])
def getData():
    return jsonify({"data": users})

@app.route('/community', methods=["GET"])
def getData():
    return jsonify({"data": community})

####
# get request by ID
# 

@app.route('/markers/<int:data_id>', methods=["GET"])
def getDataId(data_id):
    dato_encontrado = [dato for dato in markers if dato['id'] == data_id]
    return jsonify({"dato": dato_encontrado})

@app.route('/users/<int:data_id>', methods=["GET"])
def getDataId(data_id):
    dato_encontrado = [dato for dato in users if dato['id'] == data_id]
    return jsonify({"dato": dato_encontrado})

@app.route('/community/<int:data_id>', methods=["GET"])
def getDataId(data_id):
    dato_encontrado = [dato for dato in community if dato['id'] == data_id]
    return jsonify({"dato": dato_encontrado})

####
# Set request by ID
# 

@app.route('/markers', methods=['POST'])
def addData():
    new_data = {
        "id": request.json['id'],
        "latitud": request.json['latitud'],
        "longitud": request.json['longitud'],
        "peligro": request.json['peligro'],
        "fecha": request.json['fecha'],
        "hora": request.json['hora'],
        "mensaje": request.json['mensaje'],
        "ubicacion": request.json['ubicacion'],
        "votos": request.json['votos'],
        "ultimaModificacion": request.json['ultimaModificacion'],
    }
    markers.append(new_data)
    return jsonify({"message": "Dato agregado",
                    "dato": markers})

@app.route('/users', methods=['POST'])
def addData():
    new_data = {
        "id": request.json['id'],
        "email": request.json['email'],
        "friends": request.json['friends']
    }
    users.append(new_data)
    return jsonify({"message": "Dato agregado",
                    "dato": users})

@app.route('/community', methods=['POST'])
def addData():
    new_data = {
        "id": request.json['id'],
        "name": request.json['name'],
        "participantes": request.json['participantes'],
        "messages": request.json['messages']
    }
    community.append(new_data)
    return jsonify({"message": "Dato agregado",
                    "dato": community})

if __name__ == '__main__':
    app.run()