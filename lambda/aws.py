import boto3
import random
import requests
from datetime import datetime, timedelta
from ec2_metadata import ec2_metadata
import requests
import pytz

class AWSClient:
    def __init__(self):
        self.config = None
        self.key = "AKIA2YDCPYNJFV3KUWEJ"
        self.secret = "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"
        self.region = "us-east-1"
        self.cloudwatch = boto3.client('cloudwatch', aws_access_key_id=self.key, aws_secret_access_key=self.secret, region_name=self.region)
        self.ec2 = boto3.resource('ec2', aws_access_key_id=self.key, aws_secret_access_key=self.secret, region_name=self.region)
        # self.instanceId = self.get_my_instanceid()
    
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
    
    def put_statistics(self, num, sz, req, hit_rate, miss_rate, timestamp, id=None):
        if not id:
            id = self.instance_id
        self.put_data(id, 'NumberOfItems', num, timestamp)
        self.put_data(id, 'TotalSize', sz, timestamp)
        self.put_data(id, 'NumberOfRequests', req, timestamp)
        self.put_data(id, 'HitRate', hit_rate, timestamp)
        self.put_data(id, 'MissRate', miss_rate, timestamp)
    
    def get_aggregate_metric(self):
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=30)
        def get_single_aggregate_attr(attribute):
            response = self.cloudwatch.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': 'statistics',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'Memcache',
                                'MetricName': attribute,
                                'Dimensions': [{'Name': 'InstanceId', 'Value': 'aggregate'}]
                            },
                            'Period': 60,
                            'Stat': 'Sum'
                        },
                    },
                ],
                StartTime = start_time,
                EndTime = end_time,
                ScanBy= 'TimestampAscending',
                # LabelOptions={'Timezone': '+0500'}
            )        
            values = response['MetricDataResults'][0]['Values']
            timestamps = response['MetricDataResults'][0]['Timestamps']
            return (values, timestamps)

        metric = {}
        metric['NumberOfItems'], _ = get_single_aggregate_attr('NumberOfItems')
        metric['TotalSize'], _ = get_single_aggregate_attr('TotalSize')
        metric['NumberOfRequests'], _ = get_single_aggregate_attr('NumberOfRequests')
        metric['NumberOfItems'], _ = get_single_aggregate_attr('NumberOfItems')
        metric['HitRate'], _ = get_single_aggregate_attr('HitRate')
        metric['MissRate'], _ = get_single_aggregate_attr('MissRate')
        metric['NumberOfWorkers'], metric['timestamps'] = get_single_aggregate_attr('NumberOfWorkers')
        est = pytz.timezone('US/Eastern')
        metric['timestamps'] = [t.astimezone(tz=est) for t in metric['timestamps']]
        metric['simpletime'] = [t.strftime("%H:%M") for t in metric['timestamps']]
        return metric
    
    def get_data(self, instanceId, attribute, start_time, end_time):
        response = self.cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'statistics',
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
                        'Period': 5,
                        'Stat': 'Sum'
                    },
                },
            ],
            StartTime = start_time,
            EndTime = end_time
        )

        response = response['MetricDataResults'][0]
        msg = {
            'Label': response['Label'], 
            'Timestamps': response['Timestamps'],
            'Values': response['Values'] 
            }
        return msg
        
    def get_statistics(self, instanceId, start_time, end_time):
        num = self.get_data(instanceId, 'NumberOfItems', start_time, end_time)
        sz = self.get_data(instanceId, 'TotalSize', start_time, end_time)
        req = self.get_data(instanceId, 'NumberOfRequests', start_time, end_time)
        hit_rate = self.get_data(instanceId, 'HitRate', start_time, end_time)
        miss_rate = self.get_data(instanceId, 'MissRate', start_time, end_time)
        print(req)
    
    
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

    # def _get_tag_instances(self, tag_name='name', tag_val='memcache'):
    #     instances = []
    #     custom_filter = [{
    #         'Name': 'tag:' + tag_name,
    #         'Values': [tag_val]}]
    #     response = self.ec2.describe_instances(Filters=custom_filter)        
    #     reservations = response['Reservations']
    #     print(reservations)
    #     print(len(reservations))
    #     print(len(reservations[0]['Instances']))
    #     return None 
    #     for reservation in reservations:
    #         if len(reservation['Instances']) > 0:
    #             instances.append({
    #              'Id': reservation['Instances'][0]['InstanceId'],
    #              'State': reservation['Instances'][0]['State']['Name']
    #             #  'IP': reservation['Instances'][0]['PublicIpAddress']
    #             })
    #     return instances
    
    def grow_by_1(self):
        running = self.get_state_instances('running')
        if len(running) == 8:
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
        response = requests.post('http://192.168.2.35:5000/uhash_add', json={'id': instance.id,'ip': ip})

        return {'msg': f'[SUCCESS] EC2 instance {instance.id} has been started'}

    def grow_by_ratio(self, expand_ratio):
        eRatio = expand_ratio - 1.0
        running = self.get_state_instances('running')
        n_grow = round(len(running) * eRatio)
        for i in range(n_grow):
            self.grow_by_1()
        return {'msg': "grow by ratio finished"}

    def shrink_by_1(self):
        running = self.get_state_instances('running')
        if len(running) <= 1:
            return {'msg': '[FAIL] Current instance number: 1'}
        id = running[0]['Id']

        instance = self.ec2.Instance(running[0]['Id'])
        ip = "http://" + instance.public_ip_address + ':5001'
        instance.stop()
        print(f'Stoping EC2 instance {instance.id}...')
        instance.wait_until_stopped()
        print(f'EC2 instance {instance.id} has been stopped')

        response = requests.post('http://192.168.2.35:5000/uhash_shrink', json={'id': instance.id, 'ip': ip})

        return {'msg': f'[SUCCESS] EC2 instance {instance.id} has been stopped'}

    def shrink_by_ratio(self, shrink_ratio):
        sRatio = shrink_ratio
        running = self.get_state_instances('running')
        n_shrink = round(len(running) * sRatio)
        for i in range(n_shrink):
            self.shrink_by_1()
        return {'msg': "shrink by ratio finished"}

    def get_aggregate_metric(self):
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=30)
        def get_single_aggregate_attr(attribute):
            response = self.cloudwatch.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': 'statistics',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'Memcache',
                                'MetricName': attribute,
                                'Dimensions': [{'Name': 'InstanceId', 'Value': 'aggregate'}]
                            },
                            'Period': 60,
                            'Stat': 'Sum'
                        },
                    },
                ],
                StartTime = start_time,
                EndTime = end_time,
                ScanBy= 'TimestampAscending',
                # LabelOptions={'Timezone': '+0500'}
            )        
            values = response['MetricDataResults'][0]['Values']
            timestamps = response['MetricDataResults'][0]['Timestamps']
            # print(attribute, values, timestamps)
            return (values, timestamps)

        metric = {}
        metric['NumberOfItems'], _ = get_single_aggregate_attr('NumberOfItems')
        metric['TotalSize'], _ = get_single_aggregate_attr('TotalSize')
        metric['NumberOfRequests'], _ = get_single_aggregate_attr('NumberOfRequests')
        metric['NumberOfItems'], _ = get_single_aggregate_attr('NumberOfItems')
        metric['HitRate'], _ = get_single_aggregate_attr('HitRate')
        metric['MissRate'], _ = get_single_aggregate_attr('MissRate')
        metric['NumberOfWorkers'], metric['timestamps'] = get_single_aggregate_attr('NumberOfWorkers')
        est = pytz.timezone('US/Eastern')
        metric['timestamps'] = [t.astimezone(tz=est) for t in metric['timestamps']]
        metric['simpletime'] = [t.strftime("%H:%M") for t in metric['timestamps']]
        return metric


        
if __name__ == '__main__':
    print("test")
    
    awscli = AWSClient()
    
    # myid = awscli.get_my_instanceid()
    # end = datetime.now()
    # start = end - timedelta(minutes=10) 
    # print(end, start)
    # awscli.get_statistics(myid, start, end)

    running = awscli.get_state_instances('running')
    stopped = awscli.get_state_instances('stopped')

    print(running)
    print(stopped)

    # ret = awscli.grow_by_1()
    # print(ret['msg'])
