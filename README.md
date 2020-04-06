# DataOps_demo
This repository is in construction, it will describe how to automate data ingestion, analytics and feedback loop via DevOps / DataOps
No FinOps will be considered here, instead I will use different stack even if I don't need all of them, just to demonstrate integration between technology

## Technology used
* Cloud Composer
* Cloud Function
* Cloud Scheduler
* Stackdriver
* BigQuery
* Cloud Storage
* Cloud Build
* Dataflow
* Dataproc
* Datastudio

## Tweets collection every minutes using Cloud Scheduler & Cloud Function
Two basic [Cloud Function](https://github.com/mlanciau/DataOpsDemo/tree/master/cloud_function) to collect tweets from [twitter API](https://python-twitter.readthedocs.io/en/latest/), one is scheduled every minute thanks to [Cloud Scheduler](https://cloud.google.com/scheduler), one respond to [Google Cloud Storage Triggers](https://cloud.google.com/functions/docs/calling/storage), then every day this Cloud Composer [DAG](https://github.com/mlanciau/DataOpsDemo/blob/master/composer/twitter_google_cloud.py) load files thanks to [Dataflow](https://github.com/mlanciau/DataOpsDemo/blob/master/dataflow/twitter-google-dataflow.py) to BigQuery

## Collect your twitter timeline every hour with Cloud Composer
Simple [DAG](https://github.com/mlanciau/DataOpsDemo/blob/master/composer/twitter_mytimeline.py) to load your twitter timeline every hour, using some powerful features of Cloud Composer
* Airflow [variable](https://cloud.google.com/composer/docs/concepts/cloud-storage), [XComs](https://airflow.apache.org/docs/stable/concepts.html#xcoms), [bi-directionnal folder](https://cloud.google.com/composer/docs/concepts/cloud-storage)
* [Airflow python Operator](https://cloud.google.com/composer/docs/how-to/using/writing-dags#pythonoperator)
* [Airflow bash Operator](https://cloud.google.com/composer/docs/how-to/using/writing-dags#bashoperator) with gcloud, bq, gsutil and kubectl installed

## ETL with Dataproc, Dataflown, Cloud Storage and BigQuery
TODO

## Automatic CI / CD with Cloud Build and Stackdriver
TODO
