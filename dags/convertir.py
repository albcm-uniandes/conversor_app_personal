import os

from airflow import DAG
from datetime import timedelta
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

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

task = PythonOperator(
    task_id='print',
    python_callable=convert,
    dag=dag,
)

# Operators
def convert():
    def pending_tasks():
        pass
    tasks = pending_tasks()
    for task in tasks:
        command = 'ffmpeg -i ' + str(task.file) + ' ' + str(task.new_format)
        try:
            os.system(command)
            print("Conversión realizada con exito")
        except Exception as e:
            print(e)
    print(f'{len(tasks)} Tareas ejecutadas')
