import re
from flask import Flask, jsonify, request

app = Flask(__name__)

from data import data
    
@app.route('/data', methods=["GET"])
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
        "ubicación": request.json['ubicación'],
        "votos": request.json['votos'],
        "ultimaModificación": request.json['ultimaModificación'],
    }
    data.append(new_data)
    return jsonify({"message": "Dato agregado",
                    "dato": data})

if __name__ == '__main__':
    app.run(debug=True, port=5000)