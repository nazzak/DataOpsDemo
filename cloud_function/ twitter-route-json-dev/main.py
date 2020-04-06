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

import os, datetime
from google.cloud import storage
from os import getenv

bucket_name = getenv('bucket_name')
destination_bucket_name = getenv('destination_bucket_name')

def route_json_file(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    file = event
    storage_client = storage.Client()
    source_bucket = storage_client.get_bucket(bucket_name)
    source_blob = source_bucket.get_blob(file['name'])
    if 'twitter/google/' in file['name']:
        destination_bucket = storage_client.get_bucket(destination_bucket_name)
        target_blob_name = 'twitter/google/' + str(datetime.date.today()) + '/' + os.path.basename(file['name'])
        target_blob = source_bucket.copy_blob(source_blob, destination_bucket, target_blob_name)
        print(f"Processing file: {file['name']}.")
