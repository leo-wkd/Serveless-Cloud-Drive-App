from time import sleep
import boto3
from app import dynamodbcli

def create_all():
    create_photo()
    create_cache()
    create_pool()
    sleep(10)

def create_photo():
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
    print("Create photo table in dynamodb")

def create_cache():
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
    print("Create cache table in dynamodb")

def create_pool():
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
    print("Create memnode table in dynamodb")