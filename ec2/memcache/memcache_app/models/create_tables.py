from memcache_app import db

from sqlalchemy import Column
from sqlalchemy import Integer, Float, String


class Statistics(db.Model):
    __tablename__ = 'Statistics'
    time = Column(String(100), primary_key=True)
    number = Column(Integer)
    size = Column(String(20))
    requests = Column(Integer)
    hitRate = Column(Float)
    missRate = Column(Float)

    def __repr__(self):
        return "<Statistics %r>" % self.time

class Cache(db.Model):
    __tablename__ = 'Cache'
    name = Column(String(10), primary_key=True)
    capacity = Column(Integer)
    policy = Column(String(10))

    def __repr__(self):
        return "<Cache %r>" % self.time
