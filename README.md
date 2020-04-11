# DataOps demo
This repository is in construction, I started it while staying at home during coronavirus period, it will describe how to automate data ingestion, analytics and feedback loop via DevOps / DataOps
No FinOps will be considered here, instead I will use several different stack even if I don't need all of them, just to demonstrate integration between technology

## Business requirements
Our goal here is to know more about Vanves (city where I am living) and Cloud providers (news, release, interesting blogs, outage).

## Technical requirements
This demo will focus on DataOps approach, so every component will be stored in [Github](https://github.com/mlanciau/DataOpsDemo), I will the same GCP project with prefix naming convention (-dev, -prod, but you can have several GCP project for dev, int, preprod and prod if you prefer), all installation and initialisation will be done automatically by [Cloud Build](https://cloud.google.com/cloud-build) (10x easier than Jenkins)

## Technology used

### Desktop
* (Atom)[https://atom.io/]
* (GitHub Desktop)[https://desktop.github.com/]
* (Terminal)[https://en.wikipedia.org/wiki/Terminal_(macOS)]
* (Google Cloud SDK)[https://cloud.google.com/sdk]
* (Google Chrome)[https://www.google.com/chrome/]

### Google Cloud Platform

#### File Storage
* Cloud Storage

#### Scheduling
* Cloud Composer
* Cloud Scheduler

#### Automation
* Cloud Build

#### Absolute Serverless Datawarehouse
* BigQuery

#### ETL
* Dataflow
* Dataproc
* Cloud Function

#### Reporting and log analytics
* Datastudio
* Stackdriver

## Tweets collection every minutes using Cloud Scheduler & Cloud Function
Two basic [Cloud Function](https://github.com/mlanciau/DataOpsDemo/tree/master/cloud_function) to collect tweets from [twitter API](https://python-twitter.readthedocs.io/en/latest/), one is scheduled every minute thanks to [Cloud Scheduler](https://cloud.google.com/scheduler), one respond to [Google Cloud Storage Triggers](https://cloud.google.com/functions/docs/calling/storage) to reroute the file to the right GCS bucket, then every day this Cloud Composer [DAG](https://github.com/mlanciau/DataOpsDemo/blob/master/composer/twitter_google_cloud.py) load files via [Dataflow](https://github.com/mlanciau/DataOpsDemo/blob/master/dataflow/twitter-google-dataflow.py) to BigQuery

## Collect your twitter timeline every hour with Cloud Composer
Simple [DAG](https://github.com/mlanciau/DataOpsDemo/blob/master/composer/twitter_mytimeline.py) to load your twitter timeline every hour, using some powerful features of Cloud Composer
* Airflow [variable](https://cloud.google.com/composer/docs/concepts/cloud-storage), [XComs](https://airflow.apache.org/docs/stable/concepts.html#xcoms), [bi-directionnal folder](https://cloud.google.com/composer/docs/concepts/cloud-storage), [Macros](https://airflow.apache.org/docs/stable/macros.html)
* [Airflow python Operator](https://cloud.google.com/composer/docs/how-to/using/writing-dags#pythonoperator)
* [Airflow bash Operator](https://cloud.google.com/composer/docs/how-to/using/writing-dags#bashoperator) with gcloud, bq, gsutil and kubectl already installed
* [Airflow BigQuery Operator](https://airflow.apache.org/docs/stable/integration.html#bigquery)

## ETL with Dataproc, Dataflown, Cloud Storage and BigQuery
TODO

## Automatic CI / CD with Cloud Build and Stackdriver

### Continuous integration
Goal of continuous integration is to test Data Pipeline, the simplest way to be able to trigger Data Pipeline so for this project it is done either

### Continuous delivery
Goal of Continuous delivery is to automate deployment so in this demo which is the case of Data Pipeline is to be able to copy the artifact, either code (python, SQL) but also
For this basic demo I will only focus on Cloud Build but you can go further and have a look at [Spinnaker](https://cloud.google.com/solutions/continuous-delivery-spinnaker-kubernetes-engine)
