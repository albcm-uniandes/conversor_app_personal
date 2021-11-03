from airflow import DAG
from datetime import timedelta
from airflow.operators.python import PythonOperator

from executors.convert_executor import Convert
from datetime import datetime

# These args will get passed on to the python operator
default_args = {
    'owner': 'MISO_21',
    'depends_on_past': False,
    'email': ['a.cuadrado@uniandes.edu.co'],
    'email_on_failure': False,
    "start_date": datetime(2021, 10, 23, 19, 48, 0),
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'convertor_',
    default_args=default_args,
    description='Process all upload files',
    schedule_interval='*/5 * * * *'
)

_ = Convert()

task = PythonOperator(
    task_id='convert',
    python_callable=_.run,
    dag=dag,
)
