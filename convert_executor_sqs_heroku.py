import subprocess
import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import time
import sendgrid
from sendgrid.helpers.mail import Email, Mail, To, Content
from flaskr.modelos import Tarea, Usuario

load_dotenv()

db = SQLAlchemy()
sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
hostname = os.environ['RDS_HOST']
user = os.environ['RDS_USERNAME']
password = os.environ['RDS_PASSWORD']
dbname = os.environ['RDS_DATABASE']
bucket = os.environ['BUCKET']
s3 = boto3.client("s3", aws_access_key_id=os.environ['aws_access_key_id'],
                  aws_secret_access_key=os.environ['aws_secret_access_key'],
                  aws_session_token=os.environ['aws_session_token'])
sqs = boto3.client('sqs', region_name='us-east-1', aws_access_key_id=os.environ['aws_access_key_id'],
                   aws_secret_access_key=os.environ['aws_secret_access_key'],
                   aws_session_token=os.environ['aws_session_token'])
engine = create_engine(f'postgresql://{user}:{password}@{hostname}/{dbname}')
connection = engine.connect()
session = Session(bind=connection)  # create a Session


class ConvertBySQS:
    @staticmethod
    def send_email(to: str, message: str):
        from_email = Email("test@example.com")
        to_email = To(to)
        subject = "Notificación de archivo"
        content = Content("text/plain", message)
        mail = Mail(from_email, to_email, subject, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return response

    def get_task(id) -> Tarea:
        return session.query(Tarea).filter(Tarea.id == id).first()

    def get_user(id) -> Usuario:
        return session.query(Usuario).filter(Usuario.id == id).first()

    if __name__ == "__main__":
        while True:
            time.sleep(5)
            messages = sqs.receive_message(QueueUrl=os.environ.get('QUEUE_URL'))
            print(messages)
            print(len(messages))
            if len(messages) > 1:
                for msg in messages['Messages']:
                    print(msg)
                    msg_body = msg['Body']
                    task_id = int(msg_body)
                    t = get_task(task_id)
                    print(t)
                    print(f'The message body: {msg_body}')
                    try:
                        print(t.filename)
                        command = f'ffmpeg -i ' + str(t.filename) + ' ' + \
                                  t.filename[:-3] + str(t.newformat)
                        print(command)
                        print(t.newformat)
                        s3.download_file(bucket, t.filename, t.filename)
                        print("after download")
                        subprocess.call(command, shell=True)
                        print("subir archivo")
                        with open(f'{t.filename[:-3]}{str(t.newformat)}', 'rb') as data:
                            s3.upload_fileobj(data, bucket, f'{t.filename[:-3]}{str(t.newformat)}')
                        if os.path.exists(t.filename) and os.path.exists(
                                f'{t.filename[:-3]}{str(t.newformat)}'):
                            print("Eliminando archivos")
                            os.remove(t.filename)
                            os.remove(f'{t.filename[:-3]}{str(t.newformat)}')
                        t.status = "PROCESSED"
                        session.commit()
                        print("Conversión realizada con exito")
                        sqs.delete_message(QueueUrl=os.environ.get('QUEUE_URL'), ReceiptHandle=msg['ReceiptHandle'])
                    except Exception as e:
                        # send_email(get_user(t.usuario_id).correo, "Tu archivo fallo en procesar")
                        print(e)
                        sqs.delete_message(QueueUrl=os.environ.get('QUEUE_URL'), ReceiptHandle=msg['ReceiptHandle'])
                        continue
