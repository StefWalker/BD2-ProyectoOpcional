metricas personalizadas -> creo que seria desde la pagina de grafana, descarga un json de un dashboard y lo modifica para que salgan las metricas que se ocupan

api, loader, downloader, details downloader y jatsxml processor son pods y en el .yaml en application/templates seria como producer/consumer y agrega variables de env

las carpetas de api, loader, downloader, details downloader y jatsxml processor tendrian lo de app y el dockerfile. 
Su funcionalidad se programa en el callback para consumer.

cree un docker hub para que no tengamos que estar cambiando el user del docker image (los datos son losdel correo y el user es basesdedatos2)

API puede ser producer y el resto producers y consumers (?)

kibana creo que no se ocupa




### Referencias
* https://stackoverflow.com/questions/64521556/docker-build-failed-at-downloading-mariadb
* https://stackoverflow.com/questions/48310468/how-to-connect-to-database-using-scripting-language-inside-kubernetes-cluster
* https://pynative.com/python-mysql-execute-parameterized-query-using-prepared-statement/
* https://www.tutorialworks.com/kubernetes-pod-ip/
* https://scrapeops.io/python-scrapy-playbook/scrapy-save-data-mysql/
* https://requests.readthedocs.io/en/latest/_modules/requests/exceptions/