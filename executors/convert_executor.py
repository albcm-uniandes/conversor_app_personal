import subprocess
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from flaskr.modelos.modelos import Tarea, Usuario
import os

hostname = os.environ['RDS_HOST']
user = os.environ['RDS_USERNAME']
password = os.environ['RDS_PASSWORD']
dbname = os.environ['RDS_DATABASE']

engine = create_engine(f'postgresql://{user}:{password}@{hostname}/{dbname}')
connection = engine.connect()
session = Session(bind=connection)  # create a Session


class Convert:
    @staticmethod
    def pending_tasks() -> [Tarea]:
        return session.query(Tarea).filter(Tarea.status == 'UPLOADED').all()

    @staticmethod
    def pending_emails() -> []:
        set_ = []
        for task in session.query(Tarea).filter(Tarea.status == 'UPLOADED').all():
            usuario = session.query(Usuario).filter(Usuario.id == task.usuario_id).first()
            set_.append(usuario.correo)
        return set_

    def run(self):
        tasks = self.pending_tasks()
        print(len(tasks))
        if tasks:
            for t in tasks:
                command = 'ffmpeg -i /home/estudiante/Proyecto-Grupo21-202120/archivos/' + str(t.filename) + \
                          ' /home/estudiante/Proyecto-Grupo21-202120/archivos/' + t.filename[:-3] + str(
                    t.newformat)
                try:
                    subprocess.Popen(command, shell=True)
                    t.status = "PROCESSED"
                    session.commit()
                    print("Conversión realizada con exito")
                except Exception as e:
                    print(e)
            print(f'{len(tasks)} Tareas ejecutadas')
        else:
            print(f'No hay tareas por hacer')
