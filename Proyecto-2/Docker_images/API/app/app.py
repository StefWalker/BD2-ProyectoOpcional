import time
import os
import sys
import pika
import firebase_admin
import json
from firebase_admin import credentials
from firebase_admin import db
from flask import Flask, jsonify, request
from flask_ngrok import run_with_ngrok
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
run_with_ngrok(app)

cred = credentials.Certificate('adminSecret.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://tareacorta2-2f12e-default-rtdb.firebaseio.com/'
})

@app.route('/', methods=["GET"])
def getData():
    ref = db.reference('/')
    return jsonify(ref.get())

app.run()