import threading, time
from datetime import datetime

from memcache_app import memcache, awscli
from memcache_app.models import modify_tables

def send_statistics():
    timestamp = datetime.now().replace(microsecond=0)
    strtime = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    num, sz, requests, hit_rate, miss_rate = memcache.statistics()
    sz = round(sz / (1024 * 1024), 3)
    # print(timestamp, sz, flush=True)
    awscli.put_statistics(num, sz, requests, hit_rate, miss_rate, timestamp)
    # modify_tables.upload_statistics(strtime, num, str(sz) + 'MB', requests, hit_rate, miss_rate)
    threading.Timer(5, send_statistics).start()

# single thread version
# def send_statistics(interval=5):
#     def timer():
#         nextcall = time.time()
#         while True:
#             nextcall += interval
#             yield max(nextcall - time.time(), 0)

#     def send():
#         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         # modify_tables.upload_statistics(timestamp)       
#         print(timestamp)

#     t = timer()
#     while True:
#         time.sleep(next(t))
#         send()


