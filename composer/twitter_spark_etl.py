#!/usr/bin/env python3
# Copyright 2018 Google LLC
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
from datetime import datetime, timedelta
from airflow.contrib.operators import dataproc_operator
from airflow.utils import trigger_rule
from airflow.models import Variable
import os

default_dag_args = {
    'start_date': datetime(2020, 3, 29),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'depends_on_past': False,
    'email': ['mlanciau+airflow@google.com'],
    'email_on_failure': True,
    'email_on_retry': False
}

dag = DAG(
    'twitter_spark_etl',
    schedule_interval='@daily',
    default_args=default_dag_args,
    description='ETL using ephemeral Hadoop cluster',
    dagrun_timeout=timedelta(minutes=50)
)

# Create a Cloud Dataproc cluster.
create_dataproc_cluster = dataproc_operator.DataprocClusterCreateOperator(
    task_id='create_dataproc_cluster',
    dag=dag,
    project_id=os.environ.get('GCP_PROJECT'),
    cluster_name='twitter-dataproc-mlanciau-{{ ds_nodash }}',
    num_workers=3,
    num_preemptible_workers=2,
    zone='europe-west6-c',
    master_machine_type='n1-standard-1',
    worker_machine_type='n1-standard-1',
    idle_delete_ttl=3600,
    image_version='1.4',
    storage_bucket='dataproc_dataops_tmp',
#    storage_bucket='gs://{{ var.value.v_twitter_temp_bucket }}',
    subnetwork_uri='https://www.googleapis.com/compute/v1/projects/' + os.environ.get('GCP_PROJECT') + '/regions/europe-west6/subnetworks/default',
    internal_ip_only=True #Enable Private Google Access on subnetwork 'default' gcloud compute networks subnets update default --region=europe-west6 --enable-private-ip-google-access
)

# Execute PySpark job
run_pyspark_job = dataproc_operator.DataProcPySparkOperator(
    task_id='run_pyspark_job',
    dag=dag,
    main='gs://' + Variable.get('v_composer_bucket') + '/dags/dataproc/twitterPySparkSplitting.py',
    cluster_name='twitter-dataproc-mlanciau-{{ ds_nodash }}',
    dataproc_pyspark_jars=['gs://spark-lib/bigquery/spark-bigquery-latest.jar'],
    arguments=["--dataproc=1.4", "--job_date={{ ds_nodash }}", "--bucket=dataproc_dataops_tmp"]
)

# Delete Cloud Dataproc cluster.
delete_dataproc_cluster = dataproc_operator.DataprocClusterDeleteOperator(
    task_id='delete_dataproc_cluster',
    dag=dag,
    project_id=os.environ.get('GCP_PROJECT'),
    cluster_name='twitter-dataproc-mlanciau-{{ ds_nodash }}',
    trigger_rule=trigger_rule.TriggerRule.ALL_DONE
)

create_dataproc_cluster >> run_pyspark_job >> delete_dataproc_cluster
