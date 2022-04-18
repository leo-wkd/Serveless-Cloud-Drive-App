import imp
from flask import Flask
import boto3
from app.config import Config
from uhashring import HashRing
from flask_cors import CORS

webapp = Flask(__name__)
CORS(webapp)

webapp.config.from_object(Config)
s3_client = boto3.client("s3", aws_access_key_id=webapp.config["ACCESS_KEY"], aws_secret_access_key=webapp.config["ACCESS_SECRET"], region_name=webapp.config["ZONE"])
dynamodbcli = boto3.resource('dynamodb', aws_access_key_id=webapp.config["ACCESS_KEY"], aws_secret_access_key=webapp.config["ACCESS_SECRET"], region_name=webapp.config["ZONE"])
reko_client=boto3.client('rekognition', aws_access_key_id=webapp.config["ACCESS_KEY"], aws_secret_access_key=webapp.config["ACCESS_SECRET"], region_name=webapp.config["ZONE"])
uhash = HashRing()

print("stage1")
# ip of cache for remote access
# ip_addr = "http://54.152.50.47:5001"

from app import photos
from app import cache
from app import main
from app import reko
from app.init_cache import AWSClient

from app.models import create_tables
from app.models import clear_storage
from app.models import modify_tables

# clear_storage.clear_old_contents()
# clear_storage.drop_all()
# create_tables.create_all()
init_list = modify_tables.get_ip()
for ins in init_list:
    uhash.add_node(ins)
print("stage2")

aswcli = AWSClient()
# aswcli.grow_by_1()
# uhash.add_node("http://127.0.0.1:5001")
# modify_tables.add_ins("local memcache", "http://127.0.0.1:5001") 
# remove sleep 10s when using grow_by_1
print("stage3")
