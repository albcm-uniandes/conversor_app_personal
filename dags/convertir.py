from airflow import DAG
from datetime import timedelta
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from conversor.conversor_executor import Conversor

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
    python_callable=Conversor.convert,
    dag=dag,
)
