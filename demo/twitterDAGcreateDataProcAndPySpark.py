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

# [START composer_simple]
from __future__ import print_function

# [START composer_simple_define_dag]
import datetime

from airflow import models
# [END composer_simple_define_dag]
# [START composer_simple_operators]
from airflow.contrib.operators import dataproc_operator
from airflow.utils import trigger_rule
from airflow.contrib.operators import bigquery_operator

# [END composer_simple_operators]


# [START composer_simple_define_dag]
default_dag_args = {
    # The start_date describes when a DAG is valid / can be run. Set this to a
    # fixed point in time rather than dynamically, since it is evaluated every
    # time a DAG is parsed. See:
    # https://airflow.apache.org/faq.html#what-s-the-deal-with-start-date
    'start_date': datetime.datetime(2018, 11, 7),
}

# Define a DAG (directed acyclic graph) of tasks.
# Any task you create within the context manager is automatically added to the
# DAG object.
with models.DAG(
        'createdataprocandpysparkdag',
        schedule_interval=datetime.timedelta(days=1),
        default_args=default_dag_args) as dag:

    # Create a Cloud Dataproc cluster.
    create_dataproc_cluster = dataproc_operator.DataprocClusterCreateOperator(
        task_id='create_dataproc_cluster',
        project_id='google.com:mlanciau-demo-1',
        # init_actions_uris='gs://dataproc-initialization-actions/connectors/connectors.sh',
        # metadata={'gcs-connector-version':'1.7.0','bigquery-connector-version':'0.11.0'},
        # Give the cluster a unique name by appending the date scheduled.
        # See https://airflow.apache.org/code.html#default-variables
        cluster_name='twitterdataproccluster-{{ ds_nodash }}',
        num_workers=4,
        zone='europe-west4-a',
        master_machine_type='n1-standard-1',
        worker_machine_type='n1-standard-1'
    )

    # Execute PySpark job
    run_pyspark_job = dataproc_operator.DataProcPySparkOperator(
        task_id='run_pyspark_job',
        main='gs://europe-west1-mlanciaucompos-9c3e694d-bucket/others/twitterPySparkSplitting.py',
        cluster_name='twitterdataproccluster-{{ ds_nodash }}'
    )

    # Delete Cloud Dataproc cluster.
    delete_dataproc_cluster = dataproc_operator.DataprocClusterDeleteOperator(
        task_id='delete_dataproc_cluster',
        project_id='google.com:mlanciau-demo-1',
        cluster_name='twitterdataproccluster-{{ ds_nodash }}',
        # Setting trigger_rule to ALL_DONE causes the cluster to be deleted
        # even if the Dataproc job fails.
        trigger_rule=trigger_rule.TriggerRule.ALL_DONE
    )

    # BQL demo
    run_bigquery_query = bigquery_operator.BigQueryOperator(
        task_id='run_bigquery_query',
        project_id='google.com:mlanciau-demo-1',
        bql='SELECT COUNT(DISTINCT id) FROM twitter_dataset.google_tweets_en_v3',
        use_legacy_sql=False
    )

    # [START composer_simple_relationships]
    # Define the order in which the tasks complete by using the >> and <<
    # operators. In this example, hello_python executes before goodbye_bash.
    create_dataproc_cluster >> run_pyspark_job >> run_bigquery_query >> delete_dataproc_cluster
    # [END composer_simple_relationships]
# [END composer_simple]
