import time
import os
import sys
import mariadb
import requests
import datetime
import math

# Variables de entorno
#IP = os.getenv('POD_IP')
#BIO = os.getenv('BIORXIV')
#HOSTMARIA = os.getenv('MARIADB')
#MARIAPASS = os.getenv('MARIAPASS')
#RABBIT = os.getenv('RABBITMQ')
#RABBITPASS = os.getenv('RABBITPASS')
#INQUEUE = os.getenv('INQUEUE')
#OUTQUEUE = os.getenv('OUTQUEUE')
IP = "123"
# Conexion al servicio de la base de datos Mariadb
mariaDatabase = mariadb.connect(
  host="127.0.0.1",
  port=3305,
  user="user", 
  password="user",
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
response = requests.get("https://api.biorxiv.org/covid19/0").json()

# Variable para definir el tamannio del grupo
grp_size = 100
grps = math.ceil(response["messages"][0]["total"]/grp_size)

stop = 0
connection.execute("INSERT INTO jobs(created,end,status,loader,grp_size) \
                      VALUES (?,?,?,?,?)",(datetime.datetime.now(), datetime.datetime.now(), 'In progress', str(IP), grp_size))

connection.execute("SHOW TABLES")
myresult = connection.fetchall()
print(myresult)
while stop < response["messages"][0]["total"]: 
  #connection.execute("INSERT INTO groups (id_job,create,end,stage,grp_number,status,offsetData) \
  #                    VALUES ((SELECT id FROM jobs ORDER BY id DESC LIMIT 1),?,?,?,?,?,?)",(datetime.datetime.now(), None, 'loader', 1,None, stop))
  stop += grp_size

connection.execute("SELECT * FROM groups")
for i in connection:
    print(i)
mariaDatabase.commit()