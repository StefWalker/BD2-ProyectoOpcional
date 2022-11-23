import os
import time
import pika
import mariadb
import requests
import datetime
import math

# Variables de entorno
IP = os.getenv('POD_IP')
BIO = os.getenv('BIORXIV')
HOSTMARIA = os.getenv('MARIADB')
MARIAPASS = os.getenv('MARIAPASS')
RABBIT = os.getenv('RABBITMQ')
RABBITPASS = os.getenv('RABBITPASS')
INQUEUE = os.getenv('INQUEUE')
OUTQUEUE = os.getenv('OUTQUEUE')

# Conexion a RabbitMQ
credentials = pika.PlainCredentials('user', RABBITPASS)
parameters = pika.ConnectionParameters(host = RABBIT, credentials = credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue = INQUEUE)

# Conexion al servicio de la base de datos Mariadb
mariaDatabase = mariadb.connect(
  host=HOSTMARIA,
  port=3306,
  user="user", 
  password=MARIAPASS,
  database="my_database"
)

connection = mariaDatabase.cursor()

# Crear las tablas si no existen
connection.execute("DROP TABLE IF EXISTS groups")
connection.execute("DROP TABLE IF EXISTS jobs")
connection.execute("CREATE TABLE jobs (\
                      id INT NOT NULL AUTO_INCREMENT,\
                      created DATETIME NOT NULL,\
                      status VARCHAR(45) NOT NULL,\
                      end DATETIME NOT NULL,\
                      loader VARCHAR(45) NOT NULL,\
                      grp_size INT NOT NULL,\
                      PRIMARY KEY (id)\
                  )")
connection.execute("CREATE TABLE groups (\
                      id INT NOT NULL AUTO_INCREMENT,\
                      id_job INT NOT NULL,\
                      created DATETIME NOT NULL,\
                      end DATETIME,\
                      stage VARCHAR(45) NOT NULL,\
                      grp_number INT NOT NULL,\
                      status VARCHAR(45),\
                      offsetData INT NOT NULL,\
                      PRIMARY KEY (id),\
                      FOREIGN KEY (id_job) REFERENCES jobs(id)\
                  )")

# Saco los datos del endpoint
response = requests.get(BIO).json()

# Variable para definir el tamannio del grupo
grp_size = 300
grps = math.ceil(response["messages"][0]["total"]/grp_size)

# Variables de control del offset y grp_number respectivo de cada grupo
stop = 0
grp_number = 0
# Inserta el job inicial
connection.execute("INSERT INTO jobs(created,end,status,loader,grp_size) \
                      VALUES (?,?,?,?,?)",(datetime.datetime.now(), datetime.datetime.now(), 'In progress', str(IP), grp_size))
mariaDatabase.commit()

while stop < response["messages"][0]["total"] + grp_size: 
  # Ingresa el grupo correspondiente
  connection.execute("INSERT INTO groups (id_job,created,stage,grp_number,offsetData) \
                      VALUES ((SELECT id FROM jobs ORDER BY id DESC LIMIT 1),?,?,?,?)",(datetime.datetime.now(), 'loader', grp_number, stop))
  mariaDatabase.commit()

  msg = "{id_job:{" + str(grp_number) + "}, grp_number: {" + str(grp_number) + "} }"
  channel.basic_publish(exchange = '', routing_key = INQUEUE, body = msg)
  print(msg)

  # Se actualiza las variables
  stop += grp_size
  grp_number += 1
  time.sleep(1)

print('end')