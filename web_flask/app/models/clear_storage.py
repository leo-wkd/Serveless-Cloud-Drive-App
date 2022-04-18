import os
import boto3
from time import sleep
from app import s3_client
from app import webapp
from app import dynamodbcli
'''
def clear_old_contents(dir):
    for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))
'''

def clear_old_contents():
    response = s3_client.list_objects_v2(Bucket=webapp.config["BUCKET_NAME"], Prefix="images/")
    if response.get("Contents") is None:
        return
    for object in response["Contents"]:
        s3_client.delete_object(Bucket=webapp.config["BUCKET_NAME"], Key=object["Key"])

def drop_all():
    clear_photoTable()
    clear_cacheTable()
    clear_memnodeTable()
    sleep(1)

def clear_photoTable():
    table = dynamodbcli.Table('Photo')
    response = table.scan()
    key_list = []
    for item in response['Items']:
        key_list.append(item['key'])
    for photo in key_list:
        table.delete_item(
            Key = {'key': photo}
        )

def clear_cacheTable():
    table = dynamodbcli.Table('Cache')
    response = table.scan()
    key_list = []
    for item in response['Items']:
        key_list.append(item['name'])
    for cache in key_list:
        table.delete_item(
            Key = {'name': cache}
        )

def clear_memnodeTable():
    table = dynamodbcli.Table('MemNode')
    response = table.scan()
    key_list = []
    for item in response['Items']:
        key_list.append(item['ins_id'])
    for ins in key_list:
        table.delete_item(
            Key = {'ins_id': ins}
        )
