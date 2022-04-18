from time import sleep
from unicodedata import name
from app import dynamodbcli


def get_ip():
    table = dynamodbcli.Table('MemNode')
    response = table.scan()
    ip_list = []
    for ins in response['Items']:
        ip_list.append(ins['ins_ip'])
    return ip_list

def clear_photo():
    table = dynamodbcli.Table('Photo')
    response = table.scan()
    key_list = []
    for item in response['Items']:
        key_list.append(item['key'])
    for photo in key_list:
        table.delete_item(
            Key = {'key': photo}
            )
