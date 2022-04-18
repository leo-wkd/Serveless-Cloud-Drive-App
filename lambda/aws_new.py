import boto3
from datetime import datetime, timedelta
import pytz
import requests

class AWSClient:
    def __init__(self):
        self.zappa = 'https://0wtakchfzc.execute-api.us-east-1.amazonaws.com/dev'
        self.key = "AKIA6LMAN5HVJ4ZQPVYU"
        self.secret = "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"
        self.region = "us-east-1"
        self.cloudwatch = boto3.client(
            "cloudwatch",
            aws_access_key_id=self.key,
            aws_secret_access_key=self.secret,
            region_name=self.region,
        )
        self.ec2 = boto3.resource(
            "ec2",
            aws_access_key_id=self.key,
            aws_secret_access_key=self.secret,
            region_name=self.region,
        )

    def get_lambda_metric(self, fname, attribute, start_time, end_time):
        response = self.cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    "Id": "lambda",
                    "MetricStat": {
                        "Metric": {
                            "Namespace": "AWS/Lambda",
                            "MetricName": attribute,
                            "Dimensions": [{"Name": "FunctionName", "Value": fname}],
                        },
                        "Period": 60,
                        "Stat": "Average",
                    },
                },
            ],
            StartTime=start_time,
            EndTime=end_time,
            ScanBy='TimestampAscending'
        )

        response = response['MetricDataResults'][0]
        msg = {
            'Label': response['Label'],
            'Timestamps': response['Timestamps'],
            'Values': response['Values']
        }

        est = pytz.timezone('US/Eastern')
        msg['Timestamps'] = [t.astimezone(tz=est) for t in msg['Timestamps']]
        msg['simpletime'] = [t.strftime("%H:%M") for t in msg['Timestamps']]
        return msg

    def lambda_monitor_data(self, fname):
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=30)
        duration = self.get_lambda_metric(
            fname, 'Duration', start_time, end_time)
        errors = self.get_lambda_metric(fname, 'Errors', start_time, end_time)
        return (duration, errors)

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

            response = requests.post(
                self.zappa + '/uhash_add', json={'id': id, 'ip': ip})
            print(response)

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

            response = requests.post(
                self.zappa + '/uhash_shrink', json={'id': id, 'ip': ip})
            print(response)
        if to_shrink:
            to_shrink.wait_until_stopped()

        return {'msg': "shrink by ratio finished"}


if __name__ == "__main__":
    awscli = AWSClient()
    duration, errors = awscli.lambda_monitor_data('scheduledFunc')
    print(duration)

    # sz, num = awscli.total_size_worker_num()
    # print(sz, num)
    # ret = awscli.grow_by_ratio(100)
    # print(ret)
