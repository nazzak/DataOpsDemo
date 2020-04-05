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

import datetime
from airflow import models
from airflow.contrib.operators import dataproc_operator
from airflow.utils import trigger_rule

default_dag_args = {
    'start_date': datetime(2020, 3, 29),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'depends_on_past': False,
    'email': ['mlanciau+airflow@google.com'],
    'email_on_failure': True,
    'email_on_retry': False
}

with models.DAG('twitter_spark_etl', schedule_interval=None, default_args=default_dag_args) as dag:
    # Create a Cloud Dataproc cluster.
    create_dataproc_cluster = dataproc_operator.DataprocClusterCreateOperator(
        task_id='create_dataproc_cluster',
        project_id=os.environ.get('GCP_PROJECT'),
        cluster_name='twitter-dataproc--mlanciau-{{ ds_nodash }}',
        num_workers=3,
        num_preemptible_workers=2,
        zone='europe-west6-c',
        master_machine_type='n1-standard-1',
        worker_machine_type='n1-standard-1',
        graceful_decommission_timeout='1h'
    )

    # Execute PySpark job
    run_pyspark_job = dataproc_operator.DataProcPySparkOperator(
        task_id='run_pyspark_job',
        main='/home/airflow/gcs/dataproc/twitterPySparkSplitting.py',
        cluster_name='twitter-dataproc-mlanciau-{{ ds_nodash }}'
    )

    # Delete Cloud Dataproc cluster.
    delete_dataproc_cluster = dataproc_operator.DataprocClusterDeleteOperator(
        task_id='delete_dataproc_cluster',
        project_id=os.environ.get('GCP_PROJECT'),
        cluster_name='twitter-dataproc-mlanciau-{{ ds_nodash }}',
        trigger_rule=trigger_rule.TriggerRule.ALL_DONE
    )

    create_dataproc_cluster >> run_pyspark_job >> delete_dataproc_cluster