from memcache_app import db
from memcache_app.models.create_tables import Statistics, Cache

def upload_statistics(time, num, sz, requests, hit, miss):
    data = Statistics(time=time, number=num, size=sz, requests=requests, hitRate=hit, missRate=miss)
    db.session.add(data)
    db.session.commit()

def get_config():
    config = Cache.query.filter_by(name = 'local').first()
    if not config:
        return (None, None)
    capacity = config.capacity
    policy = 1 if config.policy == 'lru' else 0
    return (capacity, policy)