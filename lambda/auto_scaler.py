from time import sleep
import boto3
import random
import requests
from datetime import datetime, timedelta
from ec2_metadata import ec2_metadata
import requests
from aws import AWSClient

if __name__ == '__main__':
    awscli = AWSClient()
    metric = awscli.get_aggregate_metric()
    ratio = metric["TotalSize"] / (5 * metric["NumberOfWorkers"])
    if ratio > 0.75:
        awscli.grow_by_ratio(1.6)
        
    elif ratio < 0.25:
        awscli.shrink_by_ratio(0.5)