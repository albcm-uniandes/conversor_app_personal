import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from airflow import DAG
from datetime import timedelta
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from flask_sqlalchemy import SQLAlchemy
from flaskr.modelos import Tarea
db = SQLAlchemy()

# engine = create_engine(f'postgresql://user:password@hostname/dbname')
#connection = engine.connect()
#session = Session(bind=connection)  # create a Session


# These args will get passed on to the python operator
default_args = {
    'owner': 'MISO_21',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['a.cuadrado@uniandes.edu.co'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'convertor',
    default_args=default_args,
    description='Process all upload files',
    schedule_interval='*/5 * * * *'
)


def pending_tasks() -> [Tarea]:
    # return session.query(Tarea).filter(Tarea.status == 'UPLOADED').all()
    pass


def convert():
    tasks = pending_tasks()
    for t in tasks:
        command = 'ffmpeg -i ' + str(t.file) + ' ' + str(t.newformat)
        try:
            os.system(command)
            print("Conversión realizada con exito")
        except Exception as e:
            print(e)
    print(f'{len(tasks)} Tareas ejecutadas')


task = PythonOperator(
    task_id='convert',
    python_callable=convert,
    dag=dag,
)
