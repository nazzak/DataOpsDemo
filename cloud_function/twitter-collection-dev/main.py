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

import base64
import twitter
from google.cloud import storage
from time import time
import json
from google.cloud import datastore
import google.cloud.exceptions
from os import getenv

consumer_key = getenv('consumer_key')
consumer_secret = getenv('consumer_secret')
access_token_key = getenv('access_token_key')
access_token_secret = getenv('access_token_secret')
bucket_name = getenv('bucket_name')

def collect_tweets(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    if pubsub_message != 'minute':
        return(0)
    datastore_client = datastore.Client()
    kind = 'twitter_metadata'
    entity_id = 'twitter_google'
    datastore_key = datastore_client.key(kind, entity_id)
    datastore_entity = None
    since_id = 0
    try:
        datastore_entity = datastore_client.get(datastore_key)
        since_id = datastore_entity['since_id']
        print('since_id : ' + str(since_id))
    except google.cloud.exceptions.NotFound:
        print('twitter_metadata not found')
    api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_token_key, access_token_secret=access_token_secret)
    search = api.GetSearch(raw_query="q=google&since_id=" + str(since_id) + "&count=100")
    storage_client = storage.Client()
    filename = 'tweets_' + str(time()) + '.json'
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob('twitter/google/' + filename)
    tweets = ''
    for tweet in search:
        tweets = tweets + json.dumps(tweet._json) + '\n'
        if tweet.id > since_id:
            since_id = tweet.id
    blob.upload_from_string(tweets)
    if datastore_entity is None:
        datastore_entity = datastore.Entity(key=datastore_key)
        datastore_entity['since_id'] = since_id
        datastore_client.put(datastore_entity)
    else:
        datastore_entity['since_id'] = since_id
        datastore_client.put(datastore_entity)
    print(filename + ' created, since_id = ' + str(since_id))
