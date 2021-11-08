# Proyecto-Grupo21-202120

## Descripción
Aplicación web que permite subir abiertamente diferentes formatos de archivos de audio y poder cambiarles su formato. MP3 - ACC - OGG - WAV – WMA

## Consideraciones para la ejecución en AWS
Para levantar los servicios requeridos ejecutrar los siguientes comandos

### Correr airflow en instancia WORKER
``airflow scheduler``

### Correr ngnix con servidor flask en producción instancia WEB SERVER
``cd /home/ubuntu/Proyecto-Grupo21-202120``

``gunicorn --bind 0.0.0.0:8081 wsgi:app &``

### Otras
- Verificar que el servicio del server NFS este habilitado, instancia FILE SERVER, en caso que no ejecutar en esta instancia ``sudo systemctl restart nfs-kernel-server``

- Utilizar las variables de entorno necesaria para la aplicación, para ello guiarse del archivo .env.example que se encuentra en raiz del proyecto
- El orden de iniciación para la solución debe empezar con el levantamiento de los servicios en la RDS, verificar estado de FILE SERVER, iniciar WEB SERVER con los comando anteriormente mencionaos y por ultimo inicializar el worker de airflow en instancia WORKER


## Consideraciones para la ejecución en Maquina Virtual UNIANDES
Para levantar los servicios requeridos ejecutrar los siguientes comandos

### Correr airflow
``airflow webserver -p 8090 &``

``airflow scheduler``

### Correr ngnix con servidor flask en producción
``cd /home/estudiante/Proyecto-Grupo21-202120``

``gunicorn --bind 0.0.0.0:8081 wsgi:app &``

## Recursos 
Para ver todos los recursos acceder a la [Wiki](https://github.com/MISW-4204-ComputacionEnNube/Proyecto-Grupo21-202120/wiki)


## Definición API REST
https://documenter.getpostman.com/view/15381667/UV5ahGkB#c141ccaa-66ee-4473-9097-e9b1d5a47b0d
