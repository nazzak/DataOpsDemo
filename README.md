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


## Collect your twitter timeline every hour with Cloud Composer
Simple [DAG](https://github.com/mlanciau/DataOpsDemo/blob/master/composer/twitter_mytimeline.py) to load your twitter timeline every hour, using some powerful features of Cloud Composer
* Airflow [variable](https://cloud.google.com/composer/docs/concepts/cloud-storage), [XComs](https://airflow.apache.org/docs/stable/concepts.html#xcoms), [bi-directionnal folder](https://cloud.google.com/composer/docs/concepts/cloud-storage)
* [Airflow python Operator](https://cloud.google.com/composer/docs/how-to/using/writing-dags#pythonoperator)
* [Airflow bash Operator](https://cloud.google.com/composer/docs/how-to/using/writing-dags#bashoperator) with gcloud, bq, gsutil and kubectl installed

## ETL with Dataproc, Dataflown, Cloud Storage and BigQuery

## Automatic CI / CD with Cloud Build and Stackdriver
