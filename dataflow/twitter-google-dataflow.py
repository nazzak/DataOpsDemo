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

import apache_beam as beam
import argparse
from math import trunc
import time
import logging
import json

def checkId(line):
    record = json.loads(line)
    filter = True
    if 'id' not in record:
        logging.info('INFO : %s', line)
        filter = False
    return filter

def ExtractFields(line):
    record = json.loads(line)
    new_record = {}
    new_record['created_at'] = record['created_at'] # core column
    new_record['lang'] = record['lang']
    new_record['id'] = record['id']
    new_record['user_id'] = record['user']['id']
    new_record['user_name'] = record['user']['name']
    new_record['user_screen_name'] = record['user']['screen_name']
    new_record['text'] = record['text']
    new_record['json'] = json.dumps(record) # non core column, will be useful for replaying data pipeline if needed
    return new_record

known_args = None
pipeline_args = None

def run():
   #job_name = 'twitter-google-dataflow-' + str(trunc(time.time()))

   argv = [
      #'--job_name=' + job_name,
      '--save_main_session',
      '--staging_location=gs://' + str(known_args.dataflow_bucket) + '/staging/',
      '--temp_location=gs://' + str(known_args.dataflow_bucket) + '/temp/',
      #'--runner=DataflowRunner',
	  #'--region=europe-west1',
	  #'--zone=europe-west6-a',
	  '--max_num_workers=4'#,
      #'--network=dev-vpc'
   ]

   p = beam.Pipeline(argv=argv + pipeline_args)
   #print('Pipeline is being created')
   input = 'gs://' + str(known_args.twitter_bucket) + '/twitter/google/' + str(known_args.job_date) + '/'

   (p
      | 'ReadMyFile' >> beam.io.ReadFromText(input)
      | 'Filter' >> beam.Filter(checkId)
      | 'ExtractFields' >> beam.Map(ExtractFields)
      | 'write' >> beam.io.WriteToBigQuery(
        table='dataops_demo_raw_dev.t_twitter_google_' + known_args.job_date.replace('-','_'),
        schema='created_at:STRING, lang:STRING, id:NUMERIC, user_id:NUMERIC, user_name:STRING, user_screen_name:STRING, text:STRING, json:STRING',
        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE
      )
   )

   p.run().wait_until_finish()

if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument('--job_date', required=True)
   parser.add_argument('--twitter_bucket', required=True)
   parser.add_argument('--dataflow_bucket', required=True)
   known_args, pipeline_args = parser.parse_known_args()
   #print(known_args)
   #print(pipeline_args)
   run()
