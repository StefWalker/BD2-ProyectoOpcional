metricas personalizadas -> creo que seria desde la pagina de grafana, 
descarga un json de un dashboard 
y lo modifica para que salgan las metricas que se ocupan

api, loader, downloader, details downloader y jatsxml processor son pods 
y en el .yaml en application/templates seria como producer/consumer 
y agrega variables de env

las carpetas de api, loader, downloader, details downloader y jatsxml processor 
tendrian lo de app y el dockerfile. 
Su funcionalidad se programa en el callback para consumer.

cree un docker hub para que no tengamos que estar cambiando el user del docker image (los datos son los
del correo y el user es basesdedatos2)

API puede ser producer y el resto producers y consumers (?)

kibana creo que no se ocupa