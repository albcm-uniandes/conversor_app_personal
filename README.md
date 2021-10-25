# Proyecto-Grupo21-202120

## Descripción
Aplicación web que permite subir abiertamente diferentes formatos de archivos de audio y poder cambiarles su formato. MP3 - ACC - OGG - WAV – WMA

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
