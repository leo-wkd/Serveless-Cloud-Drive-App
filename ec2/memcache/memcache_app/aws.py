import boto3
import random
from datetime import datetime
from ec2_metadata import ec2_metadata

class AWSClient:
    def __init__(self):
        self.config = None
        self.key = "AKIA2YDCPYNJFV3KUWEJ"
        self.secret = "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"
        self.region = "us-east-1"
        self.cloudwatch = boto3.client('cloudwatch', aws_access_key_id=self.key, aws_secret_access_key=self.secret, region_name=self.region)
        self.ec2 = boto3.client('ec2', aws_access_key_id=self.key, aws_secret_access_key=self.secret, region_name=self.region)
        self.instanceId = self.get_my_instanceid()
    
    def put_data(self, instanceId, attribute, value, time):
        response = self.cloudwatch.put_metric_data(
            Namespace='Memcache',
            MetricData=[
                {
                    'MetricName': attribute,
                    'Dimensions': [
                        {
                            'Name': 'InstanceId',
                            'Value': instanceId 
                        }
                    ],
                    'Timestamp': time,
                    'Value': value, 
                    'StorageResolution': 1 
                },
            ]
        )
        # print(response)
    
    def put_statistics(self, num, sz, req, hit_rate, miss_rate, timestamp):
        self.put_data(self.instanceId, 'NumberOfItems', num, timestamp)
        self.put_data(self.instanceId, 'TotalSize', sz, timestamp)
        self.put_data(self.instanceId, 'NumberOfRequests', req, timestamp)
        self.put_data(self.instanceId, 'HitRate', hit_rate, timestamp)
        self.put_data(self.instanceId, 'MissRate', miss_rate, timestamp)
        
    def get_data(self, instanceId, attribute, startTime, endTime):
        response = self.cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'identifier',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'Memcache',
                            'MetricName': attribute,
                            'Dimensions': [
                                {
                                    'Name': 'InstanceId',
                                    'Value': instanceId 
                                }
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Sum'
                    },
                },
            ],
            StartTime = startTime,
            EndTime = endTime
        )
        # print(response)
        
    def get_running_instanceid(self):
        ids = []
        response = self.ec2.describe_instances()
        for obj in response['Reservations']:
            for ins in obj['Instances']:
                if ins['State']['Name'] == 'running':
                    ids.append(ins['InstanceId'])
        return ids
    
    def get_my_instanceid(self):
        return ec2_metadata.instance_id 



if __name__ == '__main__':
    print("test")
    
    aws_cli = AWSClient()
    # aws_cli.get_statistics(datetime.now())
    # ids = aws_cli.get_running_instanceid()
    # print(ids)
    myid = aws_cli.get_my_instanceid()
    print(myid)