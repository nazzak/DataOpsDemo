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
import json
from os import getenv
from datetime import datetime, timedelta
import pymongo

def count_tweet_from_mongoDB(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    if pubsub_message != 'hour':
        return(0)
    mongodb_user = 'mlanciauAdmin' # getenv('mongodb_user')
    mongodb_password = '6NKePkfk90GTKq6I' # getenv('mongodb_password')
    client = pymongo.MongoClient(f'mongodb://{mongodb_user}:{mongodb_password}@mlanciau-demo-shard-00-00-6qiwr.gcp.mongodb.net:27017,mlanciau-demo-shard-00-01-6qiwr.gcp.mongodb.net:27017,mlanciau-demo-shard-00-02-6qiwr.gcp.mongodb.net:27017/db_twitter?ssl=true&replicaSet=mlanciau-demo-shard-0&authSource=admin&retryWrites=true&w=majority')
    db = client.db_twitter
    collection = db.mytimeline
    count = 0
    d = datetime.now() - timedelta(minutes=240)
    count = collection.count_documents({"date": {"$lt": d}})
    print(f'I just read {count} from MongoDB Atlas from the last 4 hours')

#count_tweet_from_mongoDB(None, None)
