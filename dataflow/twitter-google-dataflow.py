#!/usr/bin/env python3
import apache_beam as beam
import argparse
from math import trunc
import time
import json

def ExtractFields(line):
   record = json.loads(line)
   new_record = {}
   new_record['created_at'] = record['created_at']
   new_record['lang'] = record['lang']
   new_record['id'] = record['id']
   new_record['user_id'] = record['user']['id']
   new_record['user_name'] = record['user']['name']
   new_record['user_screen_name'] = record['user']['screen_name']
   new_record['text'] = record['text']
   new_record['json'] = json.dumps(record)
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
