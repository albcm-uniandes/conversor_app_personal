import subprocess
import shlex
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from O365 import Message, MSGraphProtocol, Account
from flaskr.modelos import Tarea, Usuario
import smtplib, ssl

engine = create_engine(f'postgresql://elusuario:12345@localhost:5432/conversordb')
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
                newfile = str(t.filename[:-3]) + str(t.newformat)
                command = 'ffmpeg -i /home/estudiante/Proyecto-Grupo21-202120/archivos/' + str(t.filename) + \
                          ' /home/estudiante/Proyecto-Grupo21-202120/archivos/' + t.filename[:-3] + str(
                    t.newformat)
                try:
                    subprocess.Popen(command, shell=True)
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
        destination = usuario.correo[0]
        from_email = "CONVERSOR"
        subject = "Archivo procesado\n"
        user = "grupo21.conversor@outlook.com"
        password = "Grupo211357"
        header = "To:" + destination + "\n" + "From: " + from_email + "\n" + "Subject:" + subject + "\n"
        msg = ("Se ha procesado el archivo y se ha convertido al nuevo formato"
               " descarguelo dando clic aqui "
               "http://172.23.66.31:8080/api/files/")
        context=ssl.create_default_context()
        with smtplib.SMTP("smtp.office365.com", port=587, timeout=5) as smtp:
          smtp.starttls(context=context)
          smtp.login(user,password)
          smtp.send_message(msg)
          print(f'Enviado a {usuario.correo}')
        print('Before smtp')
        smtpserver = smtplib.SMTP("smtp.office365.com", 587, timeout=5)
        smtpserver.connect("smtp.office365.com", 587)
        print('Init ehlo')
        smtpserver.ehlo()
        print('Smtp Server init passed')
        smtpserver.starttls()
        print('TTLS Started')
        smtpserver.login(user, password)
        print('Logged')
        

        mail = header + msg
        print("Este es el correo ", mail)
        smtpserver.sendmail(user, destination, mail)
        smtpserver.close()

            


if __name__ == "__main__":
    Convert().enviarCorreo(7, '')
