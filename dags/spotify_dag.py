from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from datetime import timedelta

from spotify.etl import song_etl



default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['c.mendozar@outlook.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries':1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'spotify_etl',
    default_args = default_args,
    description = 'Spotify ETL to get the song of my account',
    schedule_interval = timedelta(days = 1),
    start_date = days_ago(2),
    tags = ['spotify'],

) as dag:

    run_etl = PythonOperator(task_id = "spotify_etl" , 
                provide_context=True,
                python_callable = song_etl
                )
    
run_etl 


