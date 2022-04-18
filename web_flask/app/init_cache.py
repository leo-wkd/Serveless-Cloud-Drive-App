import boto3
import random
from datetime import datetime, timedelta
from ec2_metadata import ec2_metadata
import requests
from app import uhash
from app.models import modify_tables

class AWSClient:
    def __init__(self):
        self.config = None
        self.key = "AKIA2YDCPYNJFV3KUWEJ"
        self.secret = "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"
        self.region = "us-east-1"
        self.ec2 = boto3.resource('ec2', aws_access_key_id=self.key, aws_secret_access_key=self.secret, region_name=self.region)
    
    def get_state_instances(self, state):
        instances = []
        response = self.ec2.instances.filter(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': ['cacheImages']
                },
                {
                    'Name': 'instance-state-name',
                    'Values': [state]
                }
            ]
        ) 
        for ins in response:
            instances.append({'Id': ins.id, 'State': ins.state['Name'], 'IP': ins.public_ip_address})
        return instances

    def get_tag_instances(self, tag_name='Name', tag_val='cacheImages'):
        instances = []
        response = self.ec2.instances.filter(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': ['cacheImages']
                }
            ]
        ) 
        for ins in response:
            instances.append({'Id': ins.id, 'State': ins.state['Name'], 'IP': ins.public_ip_address})
        return instances
    
    def grow_by_1(self):
        running = self.get_state_instances('running')
        if len(running) == 1:
            return {'msg': '[FAIL] Current instance number: 8'}
        stopped = self.get_state_instances('stopped') 
        if not stopped:
            return {'msg': '[FAIL] No aviliable memcache instance'}

        instance = self.ec2.Instance(stopped[0]['Id'])
        instance.start()
        print(f'Starting EC2 instance {instance.id}...')
        instance.wait_until_running()
        print(f'EC2 instance {instance.id} has been started')

        ip = "http://" + instance.public_ip_address + ':5001'
        
        uhash.add_node(ip)
        modify_tables.add_ins(instance.id, ip)

        return {'msg': f'[SUCCESS] EC2 instance {instance.id} has been started'}
