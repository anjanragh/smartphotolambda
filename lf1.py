# import json

# def lambda_handler(event, context):
#     # TODO implement
#     print("The data has come here\n")
#     return {
#         'statusCode': 200,
#         'body': json.dumps('Hello from Lambda!')
#     }

import json
import boto3
import time
from elasticsearch import Elasticsearch

# es = Elasticsearch("https://vpc-photos-wzuwkc4uurph6brpbrpcgk7bf4.us-west-2.es.amazonaws.com")
es = Elasticsearch("https://vpc-photos-ri2a5rpbqh7xynn3dwebkbppwq.us-west-2.es.amazonaws.com")

def es_create_index(indexname):
    print("This is the index name : ",indexname)
    all_indices = es.indices.get_alias("*")
    print("These are the indices : ",all_indices)
    if indexname not in all_indices:
        es.indices.create(index=indexname)
        
def es_insert_item(indexname, bucket, name, labels):
    response = es_find_item(indexname, name)
    print(response)
    if response["total"]["value"] == 0:
        
        objToInsert = {
            'bucket':bucket,
            'name':name,
            'createdTimeStamp':time.time(),
            'labels':labels,
        }
        es.index(index=indexname, body=objToInsert)
        print("Object with name",name,"is now inserted into elasticsearch")
    else :
        print("Object of the key",name,"already exists in elasticsearch")
    
    # es.insert(index=indexname, body=objToInsert)
    
# Query code
def es_find_item(indexname, name):
    response = es.search(index=indexname, body = {"query":{"match":{"name":name}}})
    print(response)
    return response["hits"]
# Delete by query code

    
def lambda_handler(event, context):
    # TODO implement
    print("-------------")
    # print(event)
    print("-------------")
    # event = {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'us-west-2', 'eventTime': '2020-04-26T00:06:11.125Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'AS0YEWV40Q972'}, 'requestParameters': {'sourceIPAddress': '67.245.14.78'}, 'responseElements': {'x-amz-request-id': 'A35E2CFA3D3EB947', 'x-amz-id-2': 'UBtt6rKhhUIyAZZTXIXYVFQFPDFF/5gdvjCg6+KijqOmQQRUHWBVp2m3zEY6NgifskEKp0cMr/4K3YRzB5jdwb3vn2mzcaYh'}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': 'put-photo-event', 'bucket': {'name': 'photos-22', 'ownerIdentity': {'principalId': 'AS0YEWV40Q972'}, 'arn': 'arn:aws:s3:::photos-22'}, 'object': {'key': 'derpy_doges.jpg', 'size': 70560, 'eTag': '411454a744408660f043162d2e01a0e9', 'sequencer': '005EA4D0772B88BD75'}}}]}
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    photo = event['Records'][0]['s3']['object']['key']
    
    print('Bucket  : ', bucket)
    print('Photo : ', photo)
    
    client=boto3.client('rekognition')
    
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
        MaxLabels=5)

    print('Detected labels for ' + photo) 
    labels = []
    for label in response['Labels']:
        print ("Label: " + label['Name'])
        labels.append(label['Name'])
    indexname = "photos"
    es_create_index(indexname)
    es_insert_item(indexname, bucket, photo, labels)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
