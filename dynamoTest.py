from time import sleep
from turtle import update
import boto3
from numpy import delete
import requests

awskey = "AKIA2YDCPYNJFV3KUWEJ"
awssecret = "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"
awsregion = "us-east-1"

###################### Photo data #######################
def create_photo(dynamodbcli):
    table = dynamodbcli.create_table(
        TableName='Photo',
        KeySchema=[
            {
                'AttributeName': 'key',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'key',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10,
        }
    )
    # print(table.table_status)

def add_photo(dynamodbcli, key, address):
    table = dynamodbcli.Table('Photo')
    response = table.put_item(
    Item = { 
        'key': key,
        'address': address
        }
    )
    # print(response)

def search_photo(dynamodbcli, key):
    table = dynamodbcli.Table('Photo')
    response = table.get_item(
        Key={
            'key': key
        }
    )
    if "Item" in response:
        print(response['Item']['address'])
    else:
        print("No photo found")

def change_photo(dynamodbcli, key, address):
    table = dynamodbcli.Table('Photo')
    response = table.update_item(
        Key={
            'key': key
            },
        UpdateExpression="set address=:new_addr",
        ExpressionAttributeValues={
            ':new_addr': address
        },
        ReturnValues="UPDATED_NEW"
    )
    # print(response)

def query_all(dynamodbcli):
    table = dynamodbcli.Table('Photo')
    response = table.scan()
    key_list = []
    for item in response['Items']:
        key_list.append(item['key'])
    return key_list

def clear_photoTable(dynamodbcli):
    table = dynamodbcli.Table('Photo')
    existing_tables = list(dynamodbcli.tables.all())
    if table not in existing_tables:
        return
    table.delete()
    sleep(1)

###################### Cache data #######################
def create_cache(dynamodbcli):
    table = dynamodbcli.create_table(
        TableName='Cache',
        KeySchema=[
            {
                'AttributeName': 'name',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'name',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10,
        }
    )
    # print(table.table_status)

def config(dynamodbcli, capacity, policy):
    table = dynamodbcli.Table('Cache')
    response = table.scan()
    if len(response['Items']):
        table.update_item(
        Key={
            'name': "local"
            },
        UpdateExpression="set capacity=:new_cap, policy=:new_pol",
        ExpressionAttributeValues={
            ':new_cap': capacity,
            ':new_pol': policy
        },
        ReturnValues="UPDATED_NEW"
        )
    else:
        table.put_item(
        Item = { 
            'name': "local",
            'capacity': capacity,
            'policy': policy
            }
        )
        
def check_config(dynamodbcli):
    table = dynamodbcli.Table('Cache')
    response = table.scan()
    if len(response['Items']):
        print("capacity:", response['Items'][0]['capacity'])
        print("policy:", response['Items'][0]['policy'])
    else:
        print("default params")

def clear_cacheTable(dynamodbcli):
    table = dynamodbcli.Table('Cache')
    existing_tables = list(dynamodbcli.tables.all())
    if table not in existing_tables:
        return
    table.delete()
    sleep(1)

###################### Instance data #######################
def create_pool(dynamodbcli):
    table = dynamodbcli.create_table(
        TableName='MemNode',
        KeySchema=[
            {
                'AttributeName': 'ins_id',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'ins_id',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10,
        }
    )
    # print(table.table_status)

def add_ins(dynamodbcli, id, ip):
    table = dynamodbcli.Table('MemNode')
    response = table.put_item(
    Item = { 
        'ins_id': id,
        'ins_ip': ip
        }
    )
    # print(response)

def remove_ins(dynamodbcli, id):
    table = dynamodbcli.Table('MemNode')
    response = table.delete_item(
        Key = {'ins_id': id}
    )
    # print(response)

def clear_memnodeTable(dynamodbcli):
    table = dynamodb.Table('MemNode')
    existing_tables = list(dynamodbcli.tables.all())
    if table not in existing_tables:
        return
    table.delete()
    sleep(1)

if __name__ == '__main__':
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=awskey, aws_secret_access_key=awssecret, region_name=awsregion)
    public_ip_address = "54.157.5.186"
    ip = "http://" + public_ip_address + ':5001'
    id = "i-007452a3c2dfcdb9c"
    zappa_ip = 'https://di9lqtzz15.execute-api.us-east-1.amazonaws.com/dev'
    response = requests.post(zappa_ip + '/uhash_add', json={'id': id,'ip': ip})
    add_ins(dynamodb, id, ip)
    print(response)
    # create_photo(dynamodb)
    # add_photo(dynamodb, "test_key", "path/to/image.jpg")
    # search_photo(dynamodb, "test_key")
    # change_photo(dynamodb, "test_key", "path/to/test.jpg")
    # search_photo(dynamodb, "test_key")
    # print(query_all(dynamodb))
    # clear_photoTable(dynamodb)

    # create_cache(dynamodb)
    # config(dynamodb, 20, "lru")
    # check_config(dynamodb)
    # config(dynamodb, 1, "random")
    # check_config(dynamodb)
    # clear_cacheTable(dynamodb)

    # create_pool(dynamodb)
    # add_ins(dynamodb, "abcdgfega", "http://127.0.0.1:5001")
    # remove_ins(dynamodb, "abcdgfega")
    # clear_memnodeTable(dynamodb)




