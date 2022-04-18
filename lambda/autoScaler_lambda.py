import os
import boto3
import requests
from datetime import datetime, timedelta
from urllib.request import Request, urlopen

SITE = os.environ['site']  # URL of the site to check, stored in the site environment variable
EXPECTED = os.environ['expected']  # String expected to be on the page, stored in the expected environment variable
ID = os.environ['id']
SECRET = os.environ['secret']
REGION = os.environ['region']
ZAPPA = os.environ['zappa']

class AWSClient:
    def __init__(self):
        self.zappa = ZAPPA
        self.cloudwatch = boto3.client('cloudwatch', aws_access_key_id=ID, aws_secret_access_key=SECRET, region_name=REGION)
        self.ec2 = boto3.resource('ec2', aws_access_key_id=ID, aws_secret_access_key=SECRET, region_name=REGION)

    def total_size_worker_num(self):
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=2)

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
                            'Stat': 'Average'
                        },
                    },
                ],
                StartTime=start_time,
                EndTime=end_time,
            )
            return response['MetricDataResults'][0]['Values']

        total_size = get_single_aggregate_attr('TotalSize')
        worker_num = get_single_aggregate_attr(
            'NumberOfWorkers')

        if total_size:
            total_size = total_size[0]
        if worker_num:
            worker_num = worker_num[0]

        return (total_size, worker_num)

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
            instances.append(
                {'Id': ins.id, 'State': ins.state['Name'], 'IP': ins.public_ip_address})
        return instances

    def grow_by_ratio(self, expand_ratio):
        print('grow')
        eRatio = expand_ratio - 1.0
        running = self.get_state_instances('running')
        stopped = self.get_state_instances('stopped')

        n_grow = round(len(running) * eRatio)
        n_grow = min(n_grow, 8 - len(running))

        to_grow = None
        for i in range(n_grow):
            id = stopped[i]['Id']
            print(id)
            to_grow = self.ec2.Instance(id)
            to_grow.start()
            to_grow.wait_until_running()
            ip = 'http://' + to_grow.public_ip_address + ':5001'
            print(ip)

            # response = requests.post(
            #     self.zappa + '/uhash_add', json={'id': id, 'ip': ip})
            # print(response)

        return {'msg': "grow by ratio finished"}

    def shrink_by_ratio(self, shrink_ratio):
        print('shrink')
        sRatio = shrink_ratio
        running = self.get_state_instances('running')

        n_shrink = round(len(running) * sRatio)
        n_shrink = min(n_shrink, len(running) - 1)

        to_shrink = None
        for i in range(n_shrink):
            id = running[i]['Id']
            ip = 'http://' + running[i]['IP'] + ':5001'
            print(id, ip)

            to_shrink = self.ec2.Instance(id)
            to_shrink.stop()

            # response = requests.post(
            #     self.zappa + '/uhash_shrink', json={'id': id, 'ip': ip})
            # print(response)
        if to_shrink:
            to_shrink.wait_until_stopped()

        return {'msg': "shrink by ratio finished"}


def validate(res):
    '''Return False to trigger the canary

    Currently this simply checks whether the EXPECTED string is present.
    However, you could modify this to perform any number of arbitrary
    checks on the contents of SITE.
    '''
    return EXPECTED in res

def check_load(awscli):
    total_size, worker_num = awscli.total_size_worker_num()
    if not worker_num:
        return
    ratio = total_size / (5 * worker_num)
    
    if ratio > 0.75:
        awscli.grow_by_ratio(1.6)
    elif ratio < 0.25:
        awscli.shrink_by_ratio(0.5)
    return

def test(awscli):
    awscli.shrink_by_ratio(0.5)


def lambda_handler(event, context):
    print('Checking {} at {}...'.format(SITE, event['time']))
    awscli = AWSClient()
    try:
        test(awscli)
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
