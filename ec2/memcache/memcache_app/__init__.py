import imp
from flask import Flask
from memcache_app.memcache import Memcache
from flask_sqlalchemy import SQLAlchemy
from memcache_app.aws import AWSClient

webapp = Flask(__name__)
db = SQLAlchemy()
memcache = Memcache()
awscli = AWSClient()

from memcache_app import main
from memcache_app.models import create_tables, modify_tables
from memcache_app.timer import send_statistics

from memcache_app.config import Config
webapp.config.from_object(Config)

db.app = webapp
db.init_app(webapp)
# db.drop_all()
# db.create_all()

capacity, policy = modify_tables.get_config()
print("memcache config: capacity = {}, policy = {}".format(capacity, policy))
memcache.config(capacity, policy)

send_statistics()