import os
import boto3
from datetime import datetime, timedelta
from urllib.request import Request, urlopen

SITE = os.environ['site']  # URL of the site to check, stored in the site environment variable
EXPECTED = os.environ['expected']  # String expected to be on the page, stored in the expected environment variable
ID = os.environ['id']
SECRET = os.environ['secret']
REGION = os.environ['region']

class AWSClient:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch', aws_access_key_id=ID, aws_secret_access_key=SECRET, region_name=REGION)
        self.ec2 = boto3.resource('ec2', aws_access_key_id=ID, aws_secret_access_key=SECRET, region_name=REGION)
        
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
        statistics = {}
        statistics['NumberOfItems'] = self.get_data(instanceId, 'NumberOfItems', start_time, end_time)
        statistics['TotalSize'] = self.get_data(instanceId, 'TotalSize', start_time, end_time)
        statistics['NumberOfRequests'] = self.get_data(instanceId, 'NumberOfRequests', start_time, end_time)
        statistics['HitRate'] = self.get_data(instanceId, 'HitRate', start_time, end_time)
        statistics['MissRate'] = self.get_data(instanceId, 'MissRate', start_time, end_time)
        return statistics

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
                    'StorageResolution': 60
                },
            ]
        )

    def put_statistics(self, num, sz, req, hit_rate, miss_rate, worker_num, timestamp, id):
        self.put_data(id, 'NumberOfItems', num, timestamp)
        self.put_data(id, 'TotalSize', sz, timestamp)
        self.put_data(id, 'NumberOfRequests', req, timestamp)
        self.put_data(id, 'HitRate', hit_rate, timestamp)
        self.put_data(id, 'MissRate', miss_rate, timestamp)
        self.put_data(id, 'NumberOfWorkers', worker_num, timestamp)

    def send_aggregate_metric(self):
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(seconds=60)
            running = self.get_state_instances('running')
            worker_num = len(running)
            if worker_num == 0:
                print('No working memcache')
                raise IndexError 
            total_num = total_sz = total_req_this_min = miss_rate = 0
            for ins in running:
                statistics = self.get_statistics(ins['Id'], start_time, end_time)
                if not statistics['NumberOfItems']['Values']:
                    continue
                total_num += statistics['NumberOfItems']['Values'][0] # total number of items of the pool
                total_sz += statistics['TotalSize']['Values'][0] # total size of items of the pool
                req_this_min = statistics['NumberOfRequests']['Values'][0] - statistics['NumberOfRequests']['Values'][-1] # number of req in this min of a single node
                total_req_this_min += req_this_min # total number of req of the pool in this minute
                miss_prev = statistics['MissRate']['Values'][-1] * statistics['NumberOfRequests']['Values'][-1] # miss reqs in 1 min ago of a single node
                miss_now = statistics['MissRate']['Values'][0] * statistics['NumberOfRequests']['Values'][0] # miss reqs currently of a single node
                miss_rate_this_min = (miss_now - miss_prev) / req_this_min if req_this_min else 0 # miss rate of a single node during this whole mintue
                miss_rate += miss_rate_this_min
    
            miss_rate /= worker_num
            hit_rate = 100 - miss_rate if total_req_this_min else 0
    
            print('aggregate', total_num, total_sz, total_req_this_min, hit_rate, miss_rate, worker_num, end_time)
            self.put_statistics(total_num, total_sz, total_req_this_min, hit_rate, miss_rate, worker_num, end_time, 'aggregate')
    
        except IndexError:
            print('no data aviliable')

def validate(res):
    '''Return False to trigger the canary

    Currently this simply checks whether the EXPECTED string is present.
    However, you could modify this to perform any number of arbitrary
    checks on the contents of SITE.
    '''
    return EXPECTED in res


def lambda_handler(event, context):
    print('Checking {} at {}...'.format(SITE, event['time']))
    
    awscli = AWSClient()
    awscli.send_aggregate_metric()

    try:
        req = Request(SITE, headers={'User-Agent': 'AWS Lambda'})
        if not validate(str(urlopen(req).read())):
            raise Exception('Validation failed')
    except:
        print('Check failed!')
        raise
    else:
        print('Check passed!')
        return event['time']
    finally:
        print('Check complete at {}'.format(str(datetime.now())))
