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
# from airflow.contrib.operators import gcs_to_gcs
# from airflow.contrib.operators import ssh_operator #sshtunnel, paramiko
from airflow.contrib.operators import bigquery_operator
# from airflow.contrib.operators import dataflow_operator
from airflow.operators import bash_operator
from datetime import datetime, timedelta
# from airflow.models import Variable
# from airflow.operators import dagrun_operator
# import twitter # library installed directly into the environment via the pypi tab
# from google.cloud import storage
from google.cloud import bigquery
# import json
# from time import time
# import os

default_args = {
    'start_date': datetime(2020, 3, 15),
    'end_date': datetime(2020, 4, 22),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'depends_on_past': False,
    'email': ['mlanciau+airflow@google.com'],
    'email_on_failure': True,
    'email_on_retry': False
}

def bigquery_schema_update(**kwargs):
    client = bigquery.Client()
    table = client.get_table('dataops_demo_sl_dev.t_twitter_google')
    new_column_name = "source"
    original_schema = table.schema
    new_schema = original_schema[:]
    print(new_schema)
    for field in new_schema:
        if field.name == new_column_name:
            return(False)
    new_schema.append(bigquery.SchemaField(new_column_name, "STRING"))
    table.schema = new_schema
    table = client.update_table(table, ["schema"])
    return(True) # hint push the return value to the XCOM

dag = DAG(
    'migration_twitter_search_01',
    default_args=default_args,
    description='Migration with data replay with BigQuery Schema change',
    schedule_interval='@daily',
    catchup=True,
    dagrun_timeout=timedelta(minutes=30),
    max_active_runs=1
)

bigquery_schema_update = python_operator.PythonOperator(
    task_id='bigquery_schema_update',
    dag=dag,
    python_callable=bigquery_schema_update,
    provide_context=True
)

delete_sl_partition = bash_operator.BashOperator(
    task_id='delete_sl_partition',
    dag=dag,
    bash_command='''bq rm -f -t 'dataops_demo_sl_dev.t_twitter_google${{ macros.ds_format(ds, "%Y-%m-%d", "%Y%m%d") }}' ''',
)

# We can of course think of something way more complex, here we are taking advantage of the json fiel so no need to reload everything
from_raw_to_sl = bigquery_operator.BigQueryOperator(
    task_id='from_raw_to_sl',
    dag=dag,
    sql='''SELECT PARSE_TIMESTAMP('%a %b %d %H:%M:%S +0000 %E4Y', created_at) AS c_timestamp,
        CAST(PARSE_TIMESTAMP('%a %b %d %H:%M:%S +0000 %E4Y', created_at) AS date) as c_created, id, user_id, user_name,
        lang, user_screen_name, text, JSON_EXTRACT(json, '$.source') AS source
        FROM dataops_demo_raw_dev.t_twitter_google_{{ macros.ds_format(ds, "%Y-%m-%d", "%Y_%m_%d") }}''',
    destination_dataset_table='dataops_demo_sl_dev.t_twitter_google',
    write_disposition='WRITE_APPEND',
    create_disposition='CREATE_IF_NEEDED',
    time_partitioning={'type': 'DAY', 'field': 'c_created'},
    allow_large_results=True,
    use_legacy_sql=False
)

# twitter_spark_etl = dagrun_operator.TriggerDagRunOperator(
#    task_id="execute_other_dag",
#    trigger_dag_id="twitter_spark_etl",  # Ensure this equals the dag_id of the DAG to trigger
#    conf={"job_date": "{{ ds }}"}, # No need for this parameter, please check execution_date
#    execution_date="{{ ds }}",
#    dag=dag,
# )

bigquery_schema_update >> delete_sl_partition >> from_raw_to_sl
