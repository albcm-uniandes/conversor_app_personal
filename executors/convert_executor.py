import subprocess
import shlex
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

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
                command = 'ffmpeg -i /home/estudiante/Proyecto-Grupo21-202120/flaskr/archivos/' + str(t.filename) + \
                          ' /home/estudiante/Proyecto-Grupo21-202120/flaskr/archivos/' + t.filename[:-3] + str(
                    t.newformat)
                try:
                    subprocess.Popen(command, shell=True)
                    t.status = "PROCESSED"
                    session.commit()
                    self.enviarCorreo(t.usuario_id, newfile)
                    print("Conversión realizada con exito")
                except Exception as e:
                    print(e)
            print(f'{len(tasks)} Tareas ejecutadas')
        else:
            print(f'No hay tareas por hacer')

    @staticmethod
    def enviarCorreo(usuario_id, nombreArchivo):
        usuario = session.query(Usuario).filter(Usuario.id == usuario_id).first()
        ## DATOS CORREO
        user = "grupo21.conversor@outlook.com"
        password = "Grupo211357"

        to = [usuario.correo]
        print(to)
        from_email = "CONVERSOR"
        subject = "Archivo procesado\n"

        ## MENSAJE
        msg = ("Se ha procesado el archivo y se ha convertido al nuevo formato"
               " descarguelo dando clic aqui "
               "http://172.23.66.31:8080/api/files/" + nombreArchivo)

        try:
            for destination in to:
                ## REALIZAR CONEXIÓN AL CORREO
                smtpserver = smtplib.SMTP("smtp.office365.com", 587)
                smtpserver.ehlo()
                smtpserver.starttls()
                smtpserver.ehlo()
                smtpserver.login(user, password)

                ## REDACCIÓN DEL CORREO
                ## CABECERA
                header = "To:" + destination + "\n" + "From: " + from_email + "\n" + "Subject:" + subject + "\n"

                ## MENSAJE
                mail = header + msg
                print("Este es el correo ", mail)

                ## ENVIÓ
                smtpserver.sendmail(user, destination, mail)
                smtpserver.close()
                return True

        except Exception as e:
            print("ERROR EN EL ENVIÓ DEL CORREO", e)
            return False


if __name__ == "__main__":
    Convert().enviarCorreo(7, '')
