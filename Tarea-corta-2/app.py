from flask import Flask, jsonify, request
from flask_ngrok import run_with_ngrok
from flask_cors import CORS
from data import data

app = Flask(__name__)
CORS(app)

run_with_ngrok(app)
    
@app.route('/', methods=["GET"])
def getData():
    return jsonify({"data": data})

@app.route('/data/<int:data_id>', methods=["GET"])
def getDataId(data_id):
    dato_encontrado = [dato for dato in data if dato['id'] == data_id]
    return jsonify({"dato": dato_encontrado})

@app.route('/data', methods=['POST'])
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
    data.append(new_data)
    return jsonify({"message": "Dato agregado",
                    "dato": data})

if __name__ == '__main__':
    app.run()