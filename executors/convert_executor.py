import subprocess

import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from flaskr.modelos.modelos import Tarea, Usuario
import os

hostname = os.environ['RDS_HOST']
user = os.environ['RDS_USERNAME']
password = os.environ['RDS_PASSWORD']
dbname = os.environ['RDS_DATABASE']
folder = os.environ['PROCESS_FOLDER']
bucket = os.environ['BUCKET']
s3 = boto3.resource("s3")
_s3 = boto3.client("s3")

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
                command = f'ffmpeg -i {folder}' + str(t.filename) + \
                          f' {folder}' + t.filename[:-3] + str(t.newformat)
                try:
                    _s3.download_file(bucket, t.filename, t.filename)
                    subprocess.Popen(command, shell=True)
                    s3.upload_fileobj(f'{folder}{t.filename[:-3]}{str(t.newformat)}', bucket,
                                      f'{folder}{t.filename[:-3]}{str(t.newformat)}')
                    if os.path.exists(folder + t.filename) and os.path.exists(
                            f'{folder}{t.filename[:-3]}{str(t.newformat)}'):
                        os.remove(folder + t.filename)
                        os.remove(f'{folder}{t.filename[:-3]}{str(t.newformat)}')
                    t.status = "PROCESSED"
                    session.commit()
                    print("Conversión realizada con exito")
                except Exception as e:
                    print(e)
            print(f'{len(tasks)} Tareas ejecutadas')
        else:
            raise Exception('No hay tareas por hacer!')
