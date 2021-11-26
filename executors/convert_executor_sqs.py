import subprocess
import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
hostname = os.environ['RDS_HOST']
user = os.environ['RDS_USERNAME']
password = os.environ['RDS_PASSWORD']
dbname = os.environ['RDS_DATABASE']
folder = os.environ['PROCESS_FOLDER']
bucket = os.environ['BUCKET']
s3 = boto3.resource("s3")
sqs = boto3.resource('sqs')
engine = create_engine(f'postgresql://{user}:{password}@{hostname}/{dbname}')
connection = engine.connect()
session = Session(bind=connection)  # create a Session


class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    filename = db.Column(db.String(128))
    newformat = db.Column(db.String(128))
    status = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime)


class ConvertBySQS:
    @staticmethod
    def get_task(id) -> [Tarea]:
        return session.query(Tarea).filter(Tarea.id == id).first()

    if __name__ == "__main__":
        while True:
            messages = sqs.receive_message(QueueUrl=os.environ.get('QUEUE_URL'))
            for msg in messages['Messages']:
                msg_body = msg['Body']
                task_id = int(msg_body)
                t = get_task(task_id)
                print(f'The message body: {msg_body}')
                command = f'ffmpeg -i {folder}' + str(t.filename) + \
                          f' {folder}' + t.filename[:-3] + str(t.newformat)
                try:
                    s3.download_file(bucket, t.filename, t.filename)
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
