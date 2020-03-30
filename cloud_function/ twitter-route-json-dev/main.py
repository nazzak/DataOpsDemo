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
