import os
import subprocess

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from flaskr.modelos import Tarea

engine = create_engine(f'postgresql://elusuario:12345@localhost:5432/conversordb')
connection = engine.connect()
session = Session(bind=connection)  # create a Session


class Convert:
    @staticmethod
    def pending_tasks() -> [Tarea]:
        return session.query(Tarea).filter(Tarea.status == 'UPLOADED').all()

    def run(self):
        print('test 1')
        tasks = self.pending_tasks()
        print(len(tasks))
        print('test 2')
        if tasks:
            print('test 3')
            for t in tasks:
                command = 'ffmpeg -i /home/estudiante/Proyecto-Grupo21-202120/flaskr/archivos/' + str(t.filename) + \
                          ' /home/estudiante/Proyecto-Grupo21-202120/flaskr/archivos/' + t.filename[:-3] + str(t.newformat)
                print(command)
                try:
                    subprocess.call(command)
                    print("Conversión realizada con exito")
                except Exception as e:
                    print(e)
            print(f'{len(tasks)} Tareas ejecutadas')
        else:
            print(f'No hay tareas por hacer')
