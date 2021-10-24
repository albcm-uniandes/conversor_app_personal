import subprocess
import shlex
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from O365 import Message, MSGraphProtocol
from flaskr.modelos import Tarea, Usuario
import smtplib

engine = create_engine(f'postgresql://elusuario:12345@localhost:5432/conversordb')
connection = engine.connect()
session = Session(bind=connection)  # create a Session


class Convert:
    @staticmethod
    def pending_tasks() -> [Tarea]:
        return session.query(Tarea).filter(Tarea.status == 'UPLOADED').all()

    def run(self):
        tasks = self.pending_tasks()
        print(len(tasks))
        if tasks:
            for t in tasks:
                newfile = str(t.filename[:-3]) + str(t.newformat)
                command = 'ffmpeg -i /home/estudiante/Proyecto-Grupo21-202120/archivos/' + str(t.filename) + \
                          ' /home/estudiante/Proyecto-Grupo21-202120/archivos/' + t.filename[:-3] + str(
                    t.newformat)
                try:
                    subprocess.Popen(command, shell=True)
                    self.enviarCorreo(t.usuario_id, newfile)
                    print('TEST')
                    t.status = "PROCESSED"
                    session.commit()
                    print("Conversión realizada con exito")
                except Exception as e:
                    print(e)
            print(f'{len(tasks)} Tareas ejecutadas')
        else:
            print(f'No hay tareas por hacer')

    @staticmethod
    def enviarCorreo(usuario_id, nombreArchivo):
        usuario = session.query(Usuario).filter(Usuario.id == usuario_id).first()
        user = "grupo21.conversor@outlook.com"
        password = "Grupo211357"
        print('Flag')
        o365_auth = (user,password)
        m = Message(auth=o365_auth, protocol=MSGraphProtocol(), recipients=[usuario.correo])
        m.setRecipients(usuario.correo)
        m.setSubject('Archivo procesado\n')
        m.setBody("Se ha procesado el archivo y se ha convertido al nuevo formato" + "http://172.23.66.31:8080/api/files/" + nombreArchivo)
        m.sendMessage()
        print('enviardo')

            


if __name__ == "__main__":
    Convert().enviarCorreo(7, '')
