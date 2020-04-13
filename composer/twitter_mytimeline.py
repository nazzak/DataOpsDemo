#!/usr/bin/env python3

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import airflow
from airflow import DAG
from airflow.operators import python_operator
from airflow.contrib.operators import gcs_to_gcs
#from airflow.contrib.operators import ssh_operator #sshtunnel, paramiko
from airflow.contrib.operators import bigquery_operator
#from airflow.contrib.operators import dataflow_operator
from airflow.operators import postgres_operator
from airflow.operators import bash_operator
from datetime import datetime, timedelta
from airflow.models import Variable
import twitter # library installed directly into the environment via the pypi tab
#from google.cloud import storage
import json
from time import time
import os

default_args = {
    'start_date': datetime(2020, 3, 29, 13),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
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
    filename = 'tweets_mytimeline_' + str(time()) + '.json'
    with open('/home/airflow/gcs/data/mytimeline/' + filename, 'w+') as outfile: # hint local /home/airflow/gcs/data/ is bi-directional sync with the bucket / data
        for tweet in mytimeline:
            data = {}
            data['created_at'] = tweet.created_at
            data['id_str'] = tweet.id_str
            data['text'] = tweet.text
            data['truncated'] = tweet.truncated
            data['lang'] = tweet.lang
            data['user_name'] = tweet.user.name
            data['user_screen_name'] = tweet.user.screen_name
            data['user_location'] = tweet.user.location
            data['retweeted'] = tweet.retweeted
            json.dump(data, outfile)
            outfile.write('\n')
            if since_id < tweet.id:
                since_id = tweet.id
    Variable.set("v_twitter_si", since_id)
    return(filename) # hint push the return value to the XCOM

dag = DAG(
    'twitter_mytimeline',
    schedule_interval='@hourly',
    default_args=default_args,
    description='Load my timeline tweets from twitter API to BQ Serving Layer',
    dagrun_timeout=timedelta(minutes=4)
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
    source_bucket='{{ var.value.v_composer_bucket }}',
    source_object="data/mytimeline/{{task_instance.xcom_pull(task_ids='twitter_mytimeline', key='return_value')}}",  # hint get the return value to the XCOM from the twitter_search_task_id
    destination_bucket='{{ var.value.v_twitter_temp_bucket }}',
    destination_object="twitter/mytimeline/{{task_instance.xcom_pull(task_ids='twitter_mytimeline', key='return_value')}}",
    move_object=True,
)

load_data_to_bq = bash_operator.BashOperator(
    task_id='load_data_to_bq',
    dag=dag,
    bash_command='''bq load --source_format=NEWLINE_DELIMITED_JSON --replace --autodetect dataops_demo_raw_dev.t_twitter_mytimeline gs://{{ var.value.v_twitter_temp_bucket }}/twitter/mytimeline/{{task_instance.xcom_pull(task_ids='twitter_mytimeline', key='return_value')}}''',
)

# Just for demoing integration with PostgreSQL
load_data_to_pg = postgres_operator.PostgresOperator(
    task_id='load_data_to_pg',
    dag=dag,
    sql='INSERT INTO twitter_metadata VALUES(%s, %s, %s)',
    postgres_conn_id='postgres_dev',
    parameters=('dev',datetime.now(), int(Variable.get("v_twitter_si", default_var=0)))
)

from_raw_to_sl = bigquery_operator.BigQueryOperator(
    task_id='from_raw_to_sl',
    dag=dag,
    sql='''SELECT PARSE_TIMESTAMP('%a %b %d %H:%M:%S +0000 %E4Y', created_at) AS c_timestamp, CAST(PARSE_TIMESTAMP('%a %b %d %H:%M:%S +0000 %E4Y', created_at) AS date) as c_created, id_str, truncated, user_name, lang, user_screen_name, text, user_location, retweeted
        FROM dataops_demo_raw_dev.t_twitter_mytimeline''',
    destination_dataset_table='dataops_demo_sl_dev.t_twitter_mytimeline',
    write_disposition='WRITE_APPEND',
    create_disposition='CREATE_IF_NEEDED',
    time_partitioning={'type':'DAY', 'field':'c_created'},
    allow_large_results=True,
    use_legacy_sql=False
)

twitter_python >> copy_file >> [load_data_to_pg, load_data_to_bq]
load_data_to_bq >> from_raw_to_sl
