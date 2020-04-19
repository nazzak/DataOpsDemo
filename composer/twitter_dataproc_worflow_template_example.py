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
#from airflow.operators import python_operator
#from airflow.contrib.operators import gcs_to_gcs
#from airflow.contrib.operators import ssh_operator #sshtunnel, paramiko
#from airflow.contrib.operators import bigquery_operator
#from airflow.contrib.operators import dataflow_operator
from airflow.operators import bash_operator
from datetime import datetime, timedelta
from airflow.models import Variable
#from airflow.operators import dagrun_operator
#import twitter # library installed directly into the environment via the pypi tab
#from google.cloud import storage
import json
from time import time
import os

default_args = {
    'start_date': datetime(2020, 3, 15),
    'retries': 1,
    'retry_delay': timedelta(minutes=15),
    'depends_on_past': False,
    'email': ['mlanciau+airflow@google.com'],
    'email_on_failure': True,
    'email_on_retry': False
}

dag = DAG(
    'twitter_dataproc_workflow_template_example',
    default_args=default_args,
    description='Dataproc workflow example',
    schedule_interval=None,
    dagrun_timeout=timedelta(minutes=120)
)

workflow_templates_delete = bash_operator.BashOperator(
    task_id='workflow_templates_delete',
    dag=dag,
    bash_command='''gcloud dataproc workflow-templates delete template-id-test --region=europe-west1 --quiet'''
)

workflow_templates_create = bash_operator.BashOperator(
    task_id='workflow_templates_create',
    dag=dag,
    bash_command='''gcloud dataproc workflow-templates create template-id-test --region=europe-west1'''
)

workflow_templates_cluster_choice = bash_operator.BashOperator(
    task_id='workflow_templates_cluster_choice',
    dag=dag,
    bash_command='''gcloud dataproc workflow-templates set-managed-cluster template-id-test --master-machine-type n1-standard-4
      --worker-machine-type n1-standard-2
      --num-workers 2
      --cluster-name template-id-test-cluster
      --num-masters=1
      --region europe-west1
      --zone europe-west1-b'''
)

workflow_templates_instantiate = bash_operator.BashOperator(
    task_id='workflow_templates_add_py_spark',
    dag=dag,
    bash_command='''bucket_name="europe-west6-composer-dev-c353e422-bucket"
      d=2020-03-15
      gcloud dataproc workflow-templates add-job pyspark gs://${bucket_name}/dags/dataproc/twitterPySparkSplitting.py
        --step-id pyspark-template-$d
        --workflow-template template-id-test
        --jars gs://spark-lib/bigquery/spark-bigquery-latest.jar
        --region europe-west1
        -- --job_date=$d --dataproc=1.4 --bucket=dataproc_dataops_tmp'''
)

workflow_templates_instantiate = bash_operator.BashOperator(
    task_id='workflow_templates_instantiate',
    dag=dag,
    bash_command='''gcloud dataproc workflow-templates instantiate template-id-test --region=europe-west1'''
)

workflow_templates_delete >> workflow_templates_create >> workflow_templates_cluster_choice >> workflow_templates_instantiate
