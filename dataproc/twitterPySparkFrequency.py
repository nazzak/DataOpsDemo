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
from pyspark.ml.feature import HashingTF, IDF, Tokenizer
#from pyspark.ml.fpm import FPGrowth
#from pyspark.mllib.feature import Word2Vec
#from pyspark.sql.functions import length
from pyspark.sql.functions import col, size, lit
#from pyspark.sql.functions import to_date
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
  .option("filter", "c_created = '" + args.job_date + "'") \
  .load()
t_twitter_google.createOrReplaceTempView('t_twitter_google')

t_twitter_google.printSchema()
#t_twitter_google.show()

# very basic filtering and ML, 10x way to improve it, later, also all that can be done directly on GCP with BQ so this is just for demoing integration
sentenceData = spark.sql("SELECT id, regexp_replace(regexp_replace(lower(text), '[^a-zA-Z0-9#@ ]+', ' '), '[ ]+', ' ') as sentence \
                            FROM t_twitter_google \
                            WHERE lang = 'en' AND lower(text) LIKE '%google%' \
                           ")

sentenceData.show(40, False)

tokenizer = Tokenizer(inputCol="sentence", outputCol="words")
wordsData = tokenizer.transform(sentenceData)

hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=20)
featurizedData = hashingTF.transform(wordsData)

idf = IDF(inputCol="rawFeatures", outputCol="features")
idfModel = idf.fit(featurizedData)
rescaledData = idfModel.transform(featurizedData)

#rescaledData.select("id", "features").show(40, False)

rescaledData.filter(size(col("words")) > 2).show(60, False)

#model.freqItemsets.filter(size(col("items")) > 2).withColumn("c_date", lit(args.job_date).cast("date")).write.format("bigquery") \
#  .option("table","dataops_demo_ml_dev.t_twitter_google") \
#  .option("partitionField","c_date") \
#  .mode("append") \
#  .save()
