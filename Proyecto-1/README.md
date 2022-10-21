# Proyecto #1: Data Migration Platform (DMP)
> Integrantes:
>
>> 
* Max Richard Lee Chung - 2019185076 
* Miguel Ku Liang - 2019061913
* Sebastian Campos Zuñiga - 2016140230
* Dylan Stef Torres Walker - 2018135751

## Guía de instalación
El programa necesita de la aplicación "Docker" y habilitar el servicio de "Kubernetes" para tener un clúster inicial y básico, llamado "docker-desktop". La aplicación para controlar y monitorear el comportamiento del clúster de Docker se denomina "Lens". Además, se utilizarán tres carpetas para cada uno de los servicios automatizados del proyecto tales como helm_charts, consumer y producer.

### Instalación de helm_charts 
Para el desarrollo de este proyecto, se van a implementar dos helm charts principales (databases y monitoring) y una para las aplicaciones implementadas en Docker (application). Dentro del helm chart databases, se utilizó la base de datos MariaDB y Elasticsearch. Dentro del helm chart monitoring, se utilizó Grafana y Prometheus junto con el operador de Elasticsearch (eck-operator). Antes de instalar todos componentes, se debe de ubicar o crear una carpeta cualquiera para luego descargar las dependencias necesarias. Ya con la carpeta seleccionada, se ingresa a la consola de comando y realizar un "cd" a dicha carpeta y ejecutar los siguientes comandos:  

```
helm create batabases
helm create monitoring
helm create application
```

Luego de ejecutar los comandos, se debe de eliminar el contenido de la carpeta "templates" de todos los archvios generados para evitar algún problema a la hora de instalar los recursos. En este punto, se debe de gestionar las dependencias de los helm charts de databases y monitoring dentro del archivo Chart.yaml al final del códgio ya proporcionado, el cual se debe de conocer las versión, enlace del repositorio y nombre para poder extraer y descargar como un archivo comprimido los recursos de cada uno. Los repositorios se deben de buscar en Google buscando, como por ejemplo, el repositorio de Bitnami o Elasticsearch. Al conocer el enlace del repositorio, se añade a la libería de helm charts y buscar el nombre del recurso al que se quiera utilizar u actualizar como se muestra en el siguiente bloque de código.

```
helm add repo <enlace proporcionado>    # Agregar a la librería de helm charts
helm update repo <enlace proporcionado> # Actualizar el repositorio
helm search repo <recurso a buscar>     # Buscar la información del recurso
```

Al conocer los datos específicos de los recuros a utilizar, se agregan las dependencias como se observa en el siguiente apartado. Además, se agregaron variables para habilitar o deshabilitar el recurso en específico, el cual se comentará más adelante sobre cómo configurarlo. 

```
# Chart.yaml de monitoring
dependencies:
- name: kube-prometheus
  version: "8.1.11"
  repository: "https://charts.bitnami.com/bitnami"
  condition: enablePrometheus
- name: grafana
  version: "8.2.11"
  repository: "https://charts.bitnami.com/bitnami"
  condition: enableGrafana
- name: eck-operator
  version: "2.4.0"
  repository: "https://helm.elastic.co"
  condition: enableOperator
```

```
# Chart.yaml de databases
dependencies:
- name: rabbitmq
  version: "11.0.3"
  repository: "https://charts.bitnami.com/bitnami"
  condition: enableRabbitMQ
- name: mariadb
  version: "11.3.3"
  repository: "https://charts.bitnami.com/bitnami"
  condition: enableMariaDB
- name: elasticsearch
  version: "19.4.4"
  repository: "https://charts.bitnami.com/bitnami"
  condition: enableElasticsearch
```

Al tener listas las dependencias con los recursos deseados, se debe de hacer un "cd" a cada una de las carpetas generadas para poder ejecutar el siguiente comando, con el fin de "actualizar" las dependencias y que se descarguen los archivos comprimidos como se mencionó anteriormente e instalarlas. 

```
cd databases                        # Ingresa a la carpeta
helm dependency update              # Actualiza las dependencias
cd ..                               # Se sale de la carpeta
helm install databases databases    # Se instala el helm chart
```

En caso contrario

```
cd monitoring
helm dependency update
cd ..
helm install monitoring monitoring
```

Sin embargo, si se instalan directamente, las bases de datos no tendrán las configuraciones que se desea, por lo que se modificó el archivo values.yaml para dicho aspecto. Para ello, se agregaron variables para habilitar o deshabilitar dicho recurso y habilitar las métricas del servicio de monitoreo para que Prometheus pueda observarlos y notificar en Grafana.

```
  enableRabbitMQ: true
  enableMariaDB: true
```

La primera configuración es la de RabbitMQ, en donde únicamente se le agregó la contraseña y habilitar el servicio de monitoreo.

```
  rabbitmq:
    auth:
      # Se agrega un password fija para installar/desinstalar
      password: "rabbitmqpass"
    # Habilitar el servicio de monitoreo
    metrics:
      enabled: true
      serviceMonitor:
        enabled: true
```

La segunda configuración es la de MariaDB, en donde se tuvo que crear la instancia estática de una contraseña principal y un usuario con su respecta contraseña para evitar conflictos con los datos persistentes almacenados en Kubernetes. Además, se le habilitó el servicio de monitoreo. 

```
  mariadb:
    auth:
      # Se agrega un password fija para installar/desinstalar
      rootPassword: "mariadbpass"
      username: "user"
      password: "user"
    # Habilitar el servicio de monitoreo
    metrics:
      enabled: true
      serviceMonitor:
        enabled: true
```

Por último, la base de datos Elascticsearch se configuró los recursos del ordenador a utilizar por cada réplica (un máster, tres nodos de datos, un coordinador y un procesador de datos), en este caso, se optó por configurarlo a un consumo de 1Mb excepto el máster, el cual usa 2 Mb.  

```
  elasticsearch:
    # Configuracion del nodo master
    master: 
      # Numero de replicas definidas para el master
      replicaCount: 1
      resources:
        requests:
          memory: "2Mi"
          cpu: "125m"
    # Configuracion del nodo de datos
    data: 
      # Numero de replicas definidas para almacenar los datos
      replicaCount: 3
      resources:
        requests:
          memory: "1Mi"
          cpu: "125m"
    # Configuracion del nodo procesador de datos
    ingest:
      # Numero de replicas definidas para el procesador de datos
      replicaCount: 1
      resources:
        requests:
          memory: "1Mi"
          cpu: "125m"
    # Configuracion del nodo coordinador
    coordinating:
      # Numero de replicas definidas para el coordinador
      replicaCount: 1
      resources:
        requests:
          memory: "1Mi"
          cpu: "125m"
    metrics:  # Habilitar el servicio de monitoreo
      enabled: true
      serviceMonitor:
        enabled: true
```

Además, Elasticsearch necesita de forma básica un clúster y una instancia de Kibana para comunicar con la base de datos como se muestra a continuación, en el cual son aplicados como un modelo básico predefinido dentro de la carpeta de databases.

```
# Deploy an Elasticsearch cluster
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: quickstart
spec:
  version: 8.4.3
  nodeSets:
  - name: default
    count: 1
    config:
      node.store.allow_mmap: false
---
# Deploy a Kibana instance
apiVersion: kibana.k8s.elastic.co/v1
kind: Kibana
metadata:
  name: quickstart
spec:
  version: 8.4.3
  count: 1
  elasticsearchRef:
    name: quickstart
```

También, es necesario correr los siguientes comandos para tener localmente las imágenes a utilizar del clúster y la instancia de Kibana

```
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.4.3
docker pull docker.elastic.co/kibana/kibana:8.4.3
```

Ya con todos los valores definidos y recursos a utilizar se utiliza los siguientes comandos fuera de las carpetas para instalarlas dentro de Kubernetes. 

```
helm install monitoring monitoring
helm install database database
```

### Instalación del consumer y producer
texto


### Configuración de herramientas no automatizadas
#### Grafana
Configurar Grafana primero es necesario haber instalado el helm chart monitoring para tener un Pod funcional de grafana, en donde se selecciona para poder acceder al enlace con el puerto de Grafana. Al estar en la página, se le solicita un usuario, en donde el usuario predeterminado es "admin" y la contraseña se adquiere dentro del Secret "monitoring-grafana-admin", el cual es generado automáticamente. 

Una vez dentro de la aplicación, es necesario agregar a Prometheus para monitorear y alertar eventos. Dentro de la esquina inferior izquierda, se encuentra el botón de configuracíón con forma de engranaje, al darle click, se despliega la página y pestaña de "Data sources", en donde se da la opción de crear uno nuevo. La nueva ventana despliega todas las opciones de "Data Source", el cual se le da a la opción de Prometheus. Ya en la opción de ingresar los datos del nuevo recurso, es necesario conocer el enlace del Prometheus creado por el helm chart cuyo enlace es el nombre del "Service" (servicio) "monitoring-kube-prometheus-prometheus" seguido de :9090 (puerto predeterminado) y se agrega.

```
http://monitoring-kube-prometheus-prometheus:9090
```

Por último, es necesario buscar un tablero "dashboard" para poder ver todas las métricas que Prometheus monitorea en Grafana, cuyo tablero se busca uno apropiado con los datos requeridos. Dicho tablero es preferible de la misma página de Grafana para poder importarlo con un ID en la sección de "Dashboards". 

## Conclusiones
text

## Recomendaciones
text

## Referencias
* [Repositorio](https://github.com/StefWalker/BD2-TareaCorta1)
* Bitnami - MariaDB (2022) Github. Recuperdo de [MariaDB](https://github.com/bitnami/charts/tree/master/bitnami/mariadb/)
* Bitnami - RabbitMQ (2022) Github. Recuperado de [Elasticsearch](https://github.com/bitnami/charts/tree/master/bitnami/rabbitmq/)
* Elastic (2022). Elastic Cloud on Kubernetes [2.4]. Recuperado de [Elasticsearch-operator](https://www.elastic.co/guide/en/cloud-on-k8s/2.4/k8s-overview.html)