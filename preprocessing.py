from time import sleep
from turtle import update
import boto3
from numpy import delete
import requests

awskey = "AKIA2YDCPYNJFV3KUWEJ"
awssecret = "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"
awsregion = "us-east-1"

def add_ins(dynamodbcli, id, ip):
    table = dynamodbcli.Table('MemNode')
    response = table.put_item(
    Item = { 
        'ins_id': id,
        'ins_ip': ip
        }
    )
    # print(response)

if __name__ == '__main__':
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=awskey, aws_secret_access_key=awssecret, region_name=awsregion)
    public_ip_address = "18.212.189.36"
    ip = "http://" + public_ip_address + ':5001'
    id = "i-0249fb585778f7225"
    add_ins(dynamodb, id, ip)
    # zappa_ip = 'https://y2u58jm567.execute-api.us-east-1.amazonaws.com/dev'
    # response = requests.post(zappa_ip + '/uhash_add', json={'id': id,'ip': ip})
    # print(response)