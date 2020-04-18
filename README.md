# DataOps demo
This repository is **in construction**, I started it while staying at home during coronavirus period, it will describe how to automate data ingestion, analytics and feedback loop via DevOps / DataOps.
No FinOps will be considered here, instead I will use several stack even if I don't need all of them, just to demonstrate integration between technologies

## Business requirements
Our goal here is to know more about Vanves (city where I am living) and Cloud providers (news, release, interesting blogs)

## Technical requirements
This demo will focus on DataOps approach, so every component will be stored in [Github](https://github.com/mlanciau/DataOpsDemo), I will use the same GCP project with prefix naming convention (-dev, -prod, but you can have different GCP projects for dev, int, preprod and prod if you prefer), all installation and initialisation will be done automatically by [Cloud Build](https://cloud.google.com/cloud-build) (10x easier than Jenkins)

## Technology used

### Desktop
* [Atom](https://atom.io/) : Nice IDE with numerous package
* [GitHub Desktop](https://desktop.github.com/)
* [Terminal](https://en.wikipedia.org/wiki/Terminal_(macOS))
* [Google Cloud SDK](https://cloud.google.com/sdk)
* [Google Chrome](https://www.google.com/chrome/) : Your favorite browser with one native excellent feature to switch between [your personnal and professional account](https://support.google.com/chrome/answer/2364824?co=GENIE.Platform%3DDesktop&hl=en) which works amazing well with GCP
* [Python 3](https://www.python.org/downloads/) : Powerful programming language, full of library

### Google Cloud Platform
* [Cloud Storage](https://cloud.google.com/storage)
* [Cloud Firestore](https://cloud.google.com/firestore)
* [BigQuery](https://cloud.google.com/bigquery)
* [Cloud SQL](https://cloud.google.com/sql)
* [Cloud Composer](https://cloud.google.com/composer)
* [Cloud Scheduler](https://cloud.google.com/scheduler)
* [Cloud Build](https://cloud.google.com/cloud-build)
* [Dataflow](https://cloud.google.com/dataflow)
* [Dataproc](https://cloud.google.com/dataproc) : Absolute way to create autoscaling Ephemeral (or long live) Hadoop cluster in 90s for running any Hadoop / Spark application
* [Cloud Function](https://cloud.google.com/functions)
* [Datastudio](https://datastudio.google.com/navigation/reporting)
* [Stackdriver](https://cloud.google.com/products/operations)

## Tweets collection every minutes using Cloud Scheduler & Cloud Function
Two basic [Cloud Function](https://github.com/mlanciau/DataOpsDemo/tree/master/cloud_function) to collect tweets from [twitter API](https://python-twitter.readthedocs.io/en/latest/), one is scheduled every minute thanks to [Cloud Scheduler](https://cloud.google.com/scheduler), one respond to [Google Cloud Storage Triggers](https://cloud.google.com/functions/docs/calling/storage) to reroute the file to the right GCS bucket, then every day this Cloud Composer [DAG](https://github.com/mlanciau/DataOpsDemo/blob/master/composer/twitter_google_cloud.py) loads files via [Dataflow](https://github.com/mlanciau/DataOpsDemo/blob/master/dataflow/twitter-google-dataflow.py) to BigQuery

### More insight from the technical design
As this is a demo, I am using more technologies than needed but what is nice here to check is :
* [Serverless technologies](https://cloud.google.com/serverless)
   * No need to worry about underlying infrastructure (provisioning, **scaling**, performance)
   * Huge range of capabilities, from Storage, messaging services, functions to data analytics & Datawarehousing and Machine Learning
   * **Pay as you go model**
   * Several language, runtimes, frameworks, and libraries
* Optimised pricing
   * BigQuery will behind the scene [reduce the cost depending your usage](https://cloud.google.com/bigquery/pricing)
   * [Aggressive pricing](https://cloud.google.com/storage/pricing#storage-pricing) for Cloud Storage with [Object Lifecycle Management](https://cloud.google.com/storage/docs/lifecycle)
   * For each component : [Free tier](https://cloud.google.com/free) (for example for Cloud Function [first 2 million are free per month](https://cloud.google.com/functions/pricing))

## Collect your twitter timeline every hour with Cloud Composer
Simple [DAG](https://github.com/mlanciau/DataOpsDemo/blob/master/composer/twitter_mytimeline.py) to load your twitter timeline every hour, using some powerful features of Cloud Composer
* Airflow [variable](https://cloud.google.com/composer/docs/concepts/cloud-storage), [XComs](https://airflow.apache.org/docs/stable/concepts.html#xcoms), [bi-directionnal folder](https://cloud.google.com/composer/docs/concepts/cloud-storage), [macros](https://airflow.apache.org/docs/stable/macros.html) and last but not least [connection](https://airflow.apache.org/docs/stable/howto/connection/index.html)
* [Airflow python Operator](https://cloud.google.com/composer/docs/how-to/using/writing-dags#pythonoperator)
* [Airflow bash Operator](https://cloud.google.com/composer/docs/how-to/using/writing-dags#bashoperator) with gcloud, bq, gsutil and kubectl already installed
* [Airflow BigQuery Operator](https://airflow.apache.org/docs/stable/integration.html#bigquery)
* [Airflow PostgreSQL Operator](https://airflow.apache.org/docs/stable/_api/airflow/operators/postgres_operator/index.html)

### More insight from the technical design
Cloud Composer is a fully managed airflow environment so you benefit from all those advantages :
* Powerful capabilities of Python and Python libraries
* Dynamic DAG
* Kubernetes bashoperator
* Airflow Operator
* Airflow community Operator

## ETL with Dataproc, Dataflown, Cloud Storage and BigQuery
Dataflow is a fantastic engine to do ETL between multiple sources and targets on GCP. I created a basic Pipeline [here](https://github.com/mlanciau/DataOpsDemo/blob/master/dataflow/twitter-google-dataflow.py) that demo how to parse JSON file from GCS, do some filtering / data preparation and then store it in BigQuery. If you prefer to use Spark or already have a huge Hadoop legacy to migrate, you can find as well a simple Dataproc job [here](https://github.com/mlanciau/DataOpsDemo/blob/master/dataproc/twitterPySparkSplitting.py) that use [Apache Spark SQL connector for Google BigQuery](https://github.com/GoogleCloudDataproc/spark-bigquery-connector).

* Choice is yours
 *
 *
* If you would like to avoid coding, we have fantastic options for that [Cloud Data Fusion](https://cloud.google.com/data-fusion) and [Cloud Dataprep by Trifacta](https://cloud.google.com/dataprep)

## Automatic CI / CD with Cloud Build and Stackdriver

### Continuous integration
[Continuous Integration](https://en.wikipedia.org/wiki/Continuous_integration) aims to improve quality by running tests. For this demo, I am using Cloud Build capabilities to trigger either Cloud Function or Cloud Composer Airflow Dag (only on the dev environment).

### Continuous delivery
Goal of [Continuous Delivery](https://en.wikipedia.org/wiki/Continuous_delivery) is to **automate deployment** once all the tests are successful. In this demo Cloud Build, will do the proper actions (initialisation, installation, creation of BigQuery Dataset, Table) in the correct environment automatically thanks to [Build Trigger](https://cloud.google.com/cloud-build/docs/running-builds/create-manage-triggers) on the **[dev|master]** branch.

PS : To go further, you might have a look at [Spinnaker](https://cloud.google.com/solutions/continuous-delivery-spinnaker-kubernetes-engine)
