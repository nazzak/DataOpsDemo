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

from pyspark.sql import SparkSession
from pyspark.mllib.feature import HashingTF, IDF
from pyspark.mllib.fpm import FPGrowth
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--job_date", required=True)
parser.add_argument("--bucket", required=True)
parser.add_argument("--dataproc", help="Version of dataproc")
args = parser.parse_args()

spark = SparkSession \
  .builder \
  .master('yarn') \
  .appName('twitter-spark-bigquery-demo') \
  .getOrCreate()

spark.conf.set('temporaryGcsBucket', args.bucket)

print(args.job_date)

t_twitter_google = spark.read.format('bigquery') \
  .option("table", 'dataops_demo_sl_dev.t_twitter_google') \
  .option("filter", "c_created = " + args.job_date) \
  .option("filter", "lang = en") \
  .load()
t_twitter_google.createOrReplaceTempView('t_twitter_google')

t_twitter_google.printSchema()

tweets_words = t_twitter_google.rdd.flatMap(lambda row: row['text'].split(' ')) #data.map(lambda line: line.strip().split(' ')) #df.filter
model = FPGrowth.train(tweets_words, minSupport=0.2, numPartitions=50)
result = model.freqItemsets().collect()
for fi in result:
    print(fi)

# Perform word count.
#word_count = spark.sql(
#    'SELECT word, SUM(word_count) AS word_count FROM words GROUP BY word')
#word_count.show()
#word_count.printSchema()

#df.write
#  .format("bigquery")
#  .option("table","dataset.table")
#  .save()

#word_count.write.format('bigquery') \
#  .option('table', 'wordcount_dataset.wordcount_output') \
#  .save()


# from __future__ import absolute_import
# import json
# import pprint
# import subprocess
# import pyspark
# from pyspark.sql import SQLContext
#
# sc = pyspark.SparkContext()
#
# # Use the Cloud Storage bucket for temporary BigQuery export data used
# # by the InputFormat. This assumes the Cloud Storage connector for
# # Hadoop is configured.
# bucket = sc._jsc.hadoopConfiguration().get('fs.gs.system.bucket')
# project = sc._jsc.hadoopConfiguration().get('fs.gs.project.id')
# input_directory = 'gs://{}/hadoop/tmp/bigquery/pyspark_input'.format(bucket)
#
# conf = {
#     # Input Parameters.
#     'mapred.bq.project.id': project,
#     'mapred.bq.gcs.bucket': bucket,
#     'mapred.bq.temp.gcs.path': input_directory,
#     'mapred.bq.input.project.id': 'google.com:mlanciau-demo-1',
#     'mapred.bq.input.dataset.id': 'twitter_dataset',
#     'mapred.bq.input.table.id': 'google_tweets_en_v3',
# }
#
# # Output Parameters.
# output_dataset = 'twitter_dataset'
# output_table = 'google_tweets_en_v3_word'
#
# # Load data in from BigQuery.
# table_data = sc.newAPIHadoopRDD(
#     'com.google.cloud.hadoop.io.bigquery.JsonTextBigQueryInputFormat',
#     'org.apache.hadoop.io.LongWritable',
#     'com.google.gson.JsonObject',
#     conf=conf)
#
# # Perform word count.
# word_counts = (
#     table_data
#     .map(lambda record: json.loads(record[1]))
#     .map(lambda tuple: (tuple['id'], tuple['created_at'], tuple['text'].split(" ")))
#     )
#
# # Display 10 results.
# pprint.pprint(word_counts.take(10))
#
# # Stage data formatted as newline-delimited JSON in Cloud Storage.
# output_directory = 'gs://{}/hadoop/tmp/bigquery/pyspark_output'.format(bucket)
# output_files = output_directory + '/part-*'
#
# sql_context = SQLContext(sc)
# (word_counts
#  .toDF(['id', 'created_at', 'array_of_word'])
#  .write.format('json').save(output_directory))
#
# # Shell out to bq CLI to perform BigQuery import.
# subprocess.check_call(
#     'bq load --source_format NEWLINE_DELIMITED_JSON '
#     '--replace '
#     '--autodetect '
#     '{dataset}.{table} {files}'.format(
#         dataset=output_dataset, table=output_table, files=output_files
#     ).split())
#
# # Manually clean up the staging_directories, otherwise BigQuery
# # files will remain indefinitely.
# input_path = sc._jvm.org.apache.hadoop.fs.Path(input_directory)
# input_path.getFileSystem(sc._jsc.hadoopConfiguration()).delete(input_path, True)
# output_path = sc._jvm.org.apache.hadoop.fs.Path(output_directory)
# output_path.getFileSystem(sc._jsc.hadoopConfiguration()).delete(
#     output_path, True)
