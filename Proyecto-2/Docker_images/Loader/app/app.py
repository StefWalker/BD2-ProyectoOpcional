import time
import os
import sys
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
#IP = "123"
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

stop = 0
grp_number = 0
connection.execute("INSERT INTO jobs(created,end,status,loader,grp_size) \
                      VALUES (?,?,?,?,?)",(datetime.datetime.now(), datetime.datetime.now(), 'In progress', str(IP), grp_size))
mariaDatabase.commit()

while stop < response["messages"][0]["total"] + grp_size: 
  connection.execute("INSERT INTO groups (id_job,created,stage,grp_number,offsetData) \
                      VALUES ((SELECT id FROM jobs ORDER BY id DESC LIMIT 1),?,?,?,?)",(datetime.datetime.now(), 'loader', grp_number, stop))
  mariaDatabase.commit()
  stop += grp_size
  grp_number += 1

print('end')