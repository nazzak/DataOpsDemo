#!/usr/bin/env python3
import airflow
from airflow import DAG
from airflow.operators import python_operator
from airflow.contrib.operators import gcs_to_gcs
#from airflow.contrib.operators import ssh_operator #sshtunnel, paramiko
from airflow.contrib.operators import bigquery_operator
#from airflow.contrib.operators import dataflow_operator
from airflow.operators import bash_operator
from datetime import datetime, timedelta
from airflow.models import Variable
import twitter # library installed directly into the environment via the pypi tab
#from google.cloud import storage
import json
from time import time
import os

default_args = {
    'start_date': airflow.utils.dates.days_ago(0),
    'schedule_interval': '5 */4 * * *',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'depends_on_past': False,
    'email': ['mlanciau+airflow@google.com'],
    'email_on_failure': True,
    'email_on_retry': False
}

def twitter_mytimeline(**kwargs):
    since_id = int(Variable.get("v_twitter_si", default_var=0)) # getting value from Variable
    consumer_key = Variable.get("v_twitter_ck")
    consumer_secret = Variable.get("v_twitter_cs")
    access_token_key = Variable.get("v_twitter_atk")
    access_token_secret = Variable.get("v_twitter_ats")
    api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_token_key, access_token_secret=access_token_secret)
    mytimeline = api.GetHomeTimeline(count=200, since_id=since_id)
    filename = 'tweets_' + str(time()) + '.json'
    with open('/home/airflow/gcs/data/mytimeline/' + filename, 'w+') as outfile: # hint local /home/airflow/gcs/data/ is bi-directional sync with the bucket / data
        for tweet in mytimeline:
            json.dump(tweet._json, outfile)
            outfile.write('\n')
            if since_id < tweet.id:
                since_id = tweet.id
    Variable.set("v_twitter_si", since_id)
    return(filename) # hint push the return value to the XCOM

dag = DAG(
    'twitter_mytimeline',
    default_args=default_args,
    description='Load my timeline tweets from twitter API to BQ Serving Layer',
    dagrun_timeout=timedelta(minutes=60)
)

twitter_python = python_operator.PythonOperator(
    task_id='twitter_mytimeline',
    dag=dag,
    python_callable=twitter_mytimeline,
    provide_context=True
)

copy_file = gcs_to_gcs.GoogleCloudStorageToGoogleCloudStorageOperator(
    task_id='copy_from_gcs_to_gcs',
    dag=dag,
    source_bucket='{{ var.value.GCS_BUCKET }}',
    source_object="data/mytimeline/{{task_instance.xcom_pull(task_ids='twitter_mytimeline', key='return_value')}}",  # hint get the return value to the XCOM from the twitter_search_task_id
    destination_bucket='temporary_python_data',
    destination_object="twitter/mytimeline/{{task_instance.xcom_pull(task_ids='twitter_mytimeline', key='return_value')}}",
    move_object=True,
)

delete_sl_partition = bash_operator.BashOperator(
    task_id='delete_sl_partition',
    dag=dag,
    bash_command='''bq rm -f -t 'dataops_demo_sl_dev.t_twitter_mytimeline${{ macros.ds_format(ds, "%Y-%m-%d", "%Y%m%d") }}' ''',
)

twitter_python >> copy_file >> delete_sl_partition
