#!/usr/bin/env python3
import airflow
from airflow import DAG
#from airflow.operators import python_operator
#from airflow.contrib.operators import gcs_to_gcs
#from airflow.contrib.operators import ssh_operator #sshtunnel, paramiko
from airflow.contrib.operators import bigquery_operator
from airflow.contrib.operators import dataflow_operator
from airflow.operators import bash_operator
from datetime import datetime, timedelta
from airflow.models import Variable
#import twitter # library installed directly into the environment via the pypi tab
#from google.cloud import storage
import json
from time import time

default_args = {
    'start_date': datetime(2020, 3, 15),
    'schedule_interval': '@daily',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'depends_on_past': False,
    'email': ['mlanciau+airflow@google.com'],
    'email_on_failure': True,
    'email_on_retry': False
}

dag = DAG(
    'twitter_search',
    default_args=default_args,
    description='Load data from GCS to BQ Serving Layer',
    dagrun_timeout=timedelta(minutes=60)
)

load_raw_data = dataflow_operator.DataFlowPythonOperator(
    task_id='load_raw_data',
    dag=dag,
    py_file='/home/airflow/gcs/dags/dataflow/twitter-google-dataflow.py',
    #py_file='dataflow/twitter-google-dataflow.py',
    job_name='twitter-google-dataflow-{{ ds }}',
    dataflow_default_options={'project':${GCP_PROJECT}, 'region': 'europe-west1','zone':'europe-west6-a','runner':'DataflowRunner'},
    options={'job_date':'{{ ds }}', 'twitter_bucket':${twitter_bucket}, 'dataflow_bucket':${dataflow_bucket}}
)

#delete_sl_partition = bigquery_operator.BigQueryOperator( # TODO change to bq command line
#    task_id='delete_sl_partition',
#    dag=dag,
#    sql='''DELETE FROM dataops_demo_sl_dev.t_twitter_google WHERE c_created = '{{ ds }}' ''',
#    use_legacy_sql=False
#)

delete_sl_partition = bash_operator.BashOperator(
    task_id='delete_sl_partition',
    dag=dag,
    bash_command='''bq rm -f -t 'dataops_demo_sl_dev.t_twitter_google${{ macros.ds_format(ds, "%Y-%m-%d", "%Y%m%d") }}' ''',
)

from_raw_to_sl = bigquery_operator.BigQueryOperator(
    task_id='from_raw_to_sl',
    dag=dag,
    sql='''SELECT PARSE_TIMESTAMP('%a %b %d %H:%M:%S +0000 %E4Y', created_at) AS c_timestamp, CAST(PARSE_TIMESTAMP('%a %b %d %H:%M:%S +0000 %E4Y', created_at) AS date) as c_created, id, user_id, user_name, lang, user_screen_name, text
        FROM dataops_demo_raw_dev.t_twitter_google_{{ macros.ds_format(ds, "%Y-%m-%d", "%Y_%m_%d") }}''',
    destination_dataset_table='dataops_demo_sl_dev.t_twitter_google',
    write_disposition='WRITE_APPEND',
    create_disposition='CREATE_IF_NEEDED',
    time_partitioning={'type':'DAY', 'field':'c_created'},
    allow_large_results=True,
    use_legacy_sql=False
)

load_raw_data >> delete_sl_partition >> from_raw_to_sl
