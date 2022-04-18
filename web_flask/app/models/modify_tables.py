from unicodedata import name
from app import dynamodbcli

def add_photo(key, address):
    table = dynamodbcli.Table('Photo')
    response = table.put_item(
    Item = { 
        'key': key,
        'address': address
        }
    )
    # print(response)

def change_photo(key, address):
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

def search_photo(key):
    table = dynamodbcli.Table('Photo')
    response = table.get_item(
        Key={
            'key': key
        }
    )
    if "Item" in response:
        return response['Item']['address']
    else:
        return ""

def delete_photo(key):
    table = dynamodbcli.Table('Photo')
    response = table.delete_item(
        Key = {'key': key}
    )

def query_all():
    table = dynamodbcli.Table('Photo')
    response = table.scan()
    key_list = []
    for item in response['Items']:
        key_list.append(item['key'])
    return key_list

def config(capacity, policy):
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

def add_ins(id, ip):
    table = dynamodbcli.Table('MemNode')
    response = table.put_item(
    Item = { 
        'ins_id': id,
        'ins_ip': ip
        }
    )
    # print(response)

def remove_ins(id, ip):
    table = dynamodbcli.Table('MemNode')
    response = table.delete_item(
        Key = {'ins_id': id}
    )
    # print(response)

def get_ip():
    table = dynamodbcli.Table('MemNode')
    response = table.scan()
    ip_list = []
    for ins in response['Items']:
        ip_list.append(ins['ins_ip'])
    return ip_list