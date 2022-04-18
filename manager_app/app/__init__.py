import imp
from flask import Flask
import boto3

from app.config import Config
from app.aws import AWSClient
# from AutoScaler.aws import AWSClient

webapp = Flask(__name__)
webapp.config.from_object(Config)
dynamodbcli = boto3.resource('dynamodb', aws_access_key_id=webapp.config["ACCESS_KEY"], aws_secret_access_key=webapp.config["ACCESS_SECRET"], region_name=webapp.config["ZONE"])
s3_client = boto3.client("s3", aws_access_key_id=webapp.config["ACCESS_KEY"], aws_secret_access_key=webapp.config["ACCESS_SECRET"], region_name=webapp.config["ZONE"])
awscli = AWSClient()

from app import configure
from app import main
from app import display
from app import aws