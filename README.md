# DataOps demo
This repository is **in construction**, I started it while staying at home during coronavirus period, it will describe how to automate data ingestion, analytics and feedback loop via [DevOps](https://cloud.google.com/devops) / DataOps.
No FinOps will be considered here, instead I will use several stack even if I don't need all of them, just to demonstrate integration between technologies

## Business requirements
Our goal here is to know more about Vanves (city where I am living) and Cloud providers (news, release, interesting blogs)

## Technical requirements
This demo will focus on DataOps approach, so every component will be stored in [Github](https://github.com/mlanciau/DataOpsDemo), I will use the same GCP project with prefix naming convention (-dev, -prod, but you can have different GCP projects for dev, int, preprod and prod if you prefer), all installation and initialisation will be done automatically by [Cloud Build](https://cloud.google.com/cloud-build) (10x easier than Jenkins)

## Technology used

### Desktop
* [Atom](https://atom.io/) : Nice IDE with numerous package
* [GitHub Desktop](https://desktop.github.com/) : Graphical User Interface (GUI) to use Git
* [Cloud Shell](https://cloud.google.com/shell) : Cloud Shell provides you with command-line access to your cloud resources directly from your browser with Google Cloud SDK and other utilities already installed + 5 GB of persistent disk storage
* [Google Cloud SDK](https://cloud.google.com/sdk) : The Cloud SDK is a set of command-line tools for developing with Google Cloud. You can use these tools to access Compute Engine, Cloud Storage, BigQuery, and other Google Cloud services directly from the command line.
* [Google Chrome](https://www.google.com/chrome/) : Your favorite browser with one native excellent feature to switch between [your personnal and professional account](https://support.google.com/chrome/answer/2364824?co=GENIE.Platform%3DDesktop&hl=en) which works amazing well with GCP
* [Python 3](https://www.python.org/downloads/) : Powerful programming language, full of library

### Google Cloud Platform
* [Cloud Storage](https://cloud.google.com/storage) : worldwide, highly durable object storage that scales to exabytes of data
* [Cloud Firestore](https://cloud.google.com/firestore) : fast, fully managed, serverless, cloud-native NoSQL document database that simplifies storing, syncing, and querying data for your mobile, web, and IoT apps at global scale
* [BigQuery](https://cloud.google.com/bigquery) : Serverless, highly scalable, and cost-effective cloud data warehouse designed for business agility
* [Cloud SQL](https://cloud.google.com/sql) : Fully managed relational database service for MySQL, PostgreSQL, and SQL server
* [Cloud Composer](https://cloud.google.com/composer) : A fully managed workflow orchestration service built on Apache Airflow.
* [Cloud Scheduler](https://cloud.google.com/scheduler) : Fully managed enterprise-grade cron job scheduler
* [Cloud Build](https://cloud.google.com/cloud-build) : Cloud Build lets you build software quickly across all languages
* [Dataflow](https://cloud.google.com/dataflow) : Fast, serverless, unified stream and batch data processing
* [Dataproc](https://cloud.google.com/dataproc) : Absolute way to create autoscaling Ephemeral (or long live) Hadoop cluster in 90s for running any Hadoop / Spark application
* [Cloud Function](https://cloud.google.com/functions) : Google Cloud’s event-driven serverless compute platform
* [Pub/Sub](https://cloud.google.com/pubsub/) : Global messaging and event ingestion made simple
* [Datastudio](https://support.google.com/datastudio/answer/6283323?hl=en&ref_topic=6267740) : Data Studio turns your data into informative, easy to read, easy to share, and fully customizable dashboards and reports for free
* [Operations](https://cloud.google.com/products/operations) : Monitor, troubleshoot, and improve infrastructure and application performance

## Tweets collection every minutes using Cloud Scheduler & Cloud Function
Two basic [Cloud Function](https://github.com/mlanciau/DataOpsDemo/tree/master/cloud_function) to collect tweets from [twitter API](https://python-twitter.readthedocs.io/en/latest/), one is scheduled every minute thanks to [Cloud Scheduler](https://cloud.google.com/scheduler), one respond to [Google Cloud Storage Triggers](https://cloud.google.com/functions/docs/calling/storage) to reroute the file to the right GCS bucket, then every day this Cloud Composer [DAG](https://github.com/mlanciau/DataOpsDemo/blob/master/composer/twitter_google_cloud.py) loads files via [Dataflow](https://github.com/mlanciau/DataOpsDemo/blob/master/dataflow/twitter-google-dataflow.py) to BigQuery

### More insight from the technical design
As this is a demo, I am using more technologies than needed but what is nice here to check is :
* [Serverless technologies](https://cloud.google.com/serverless)
   * No need to worry about underlying infrastructure (provisioning, **scaling**, performance)
   * Huge range of capabilities, from Storage, messaging services, functions to data analytics & Datawarehousing and Machine Learning
   * Several language, runtimes, frameworks, and libraries
* Optimised pricing
   * **Pay as you go model**
   * BigQuery will behind the scene [reduce the cost depending your usage](https://cloud.google.com/bigquery/pricing)
   * [Aggressive pricing](https://cloud.google.com/storage/pricing#storage-pricing) for Cloud Storage with [Object Lifecycle Management](https://cloud.google.com/storage/docs/lifecycle)
   * [Free tier](https://cloud.google.com/free) for each component (for example for Cloud Function [first 2 million are free per month](https://cloud.google.com/functions/pricing))

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
* [Dynamic DAG](https://medium.com/google-cloud/create-a-dynamically-created-dag-and-troubleshoot-airflows-webserver-in-google-cloud-composer-290af1e3eb1b)
* [KubernetesPodOperator](https://cloud.google.com/composer/docs/how-to/using/using-kubernetes-pod-operator), useful if you require Custom Python dependencies or Binary dependencies that aren't available in the stock Cloud Composer worker image
* [Airflow Operator](https://github.com/apache/airflow/tree/master/airflow/operators)
* [Airflow contrib / community Operator](https://github.com/apache/airflow/tree/master/airflow/contrib/operators)

## ETL with Dataproc, Dataflown, Cloud Function, Cloud Storage and BigQuery
Dataflow is a fantastic engine to do ETL between multiple sources and targets on GCP. I created a basic Pipeline [here](https://github.com/mlanciau/DataOpsDemo/blob/master/dataflow/twitter-google-dataflow.py) that demo how to parse JSON file from GCS, do some filtering / data preparation and then store it in BigQuery. For the Hadoop fan, you can find as well a simple Dataproc job [here](https://github.com/mlanciau/DataOpsDemo/blob/master/dataproc/twitterPySparkSplitting.py) that use [Apache Spark SQL connector for Google BigQuery](https://github.com/GoogleCloudDataproc/spark-bigquery-connector).

### More insight from the technical design
* Choice is yours, depending on your need you can use directly
  * Cloud Function for quick action (move a file, grab data from an API, link / transform information between Pub/Sub and other Google Cloud technologies)
  * Dataproc if you prefer to use Spark or already have a huge Hadoop legacy to migrate
  * Dataflow extraordinary distributed processing backend for Open Source [Apache Beam](https://cloud.google.com/dataflow/docs/concepts/beam-programming-model) with virtually limitless capacity
  * BigQuery might be the easiest and cheapest way to do ETL / ELT with SQL, you just need to load your data first
* If you would like to avoid coding, we have fantastic options for that [Cloud Data Fusion](https://cloud.google.com/data-fusion) and [Cloud Dataprep by Trifacta](https://cloud.google.com/dataprep)

## Automatic CI / CD with Cloud Build and Operation

### Continuous integration
[Continuous Integration](https://en.wikipedia.org/wiki/Continuous_integration) aims to improve quality by running tests. For this demo, I am using Cloud Build capabilities to trigger either Cloud Function or Cloud Composer Airflow Dag (only on the dev environment).

### Continuous delivery
Goal of [Continuous Delivery](https://en.wikipedia.org/wiki/Continuous_delivery) is to **automate deployment** once all the tests are successful. In this demo Cloud Build, will do the proper actions (initialisation, installation, creation of BigQuery Dataset, Table) in the correct environment automatically thanks to [Build Trigger](https://cloud.google.com/cloud-build/docs/running-builds/create-manage-triggers) on the **[dev|master]** branch.

PS : To go further, you might have a look at [Spinnaker](https://cloud.google.com/solutions/continuous-delivery-spinnaker-kubernetes-engine)

### Monitoring
What are the basic Dashboard and alerting we need for doing DataOps :
* Error in Cloud Composer environment
* Error in Cloud Build
* Performance and performance variation of all DAGs
* Data Quality
(More details soon)

## ToDo
- [ ] Complete monitoring and alerting with Operation and log sink + BigQuery & DataStudio
- [ ] Add information about testing
- [ ] Add information about improving the speed of all steps
- [ ] Add monitoring of Business metrics / data or model quality
- [ ] Add way to initialize new environment (esp. Pre-prod and sandbox)
- [ ] Add specific data monitoring
- [ ] [Notification options to Pub/Sub](https://cloud.google.com/monitoring/support/notification-options?_ga=2.117224837.-289278821.1584538078&_gac=1.142222726.1585069485.EAIaIQobChMI4OLd-cuz6AIVSEHTCh2udgE8EAAYASAAEgJT-PD_BwE#pubsub)
- [ ] [Overview of logs exports](https://cloud.google.com/logging/docs/export)
- [ ] AutoML API
- [ ] How easy to use [Alerting Policy](https://cloud.google.com/monitoring/alerts/using-alerting-ui)
- [ ] Add Cloud SQL Proxy just for the demo
- [ ] Add information about data replay from Archive to Serling Layer thanks to [Airflow Backfill and Catchup](https://airflow.apache.org/docs/stable/scheduler.html#backfill-and-catchup)

## Stay safe !
I hope you will enjoy this demo as well as the amazing capabilities of Google Cloud Platform
Don't hesitate to [ping me](https://twitter.com/lanciaux_maxime?lang=en) if you have any question or suggestion
![Stay Safe](Stay_Safe.jpg)
