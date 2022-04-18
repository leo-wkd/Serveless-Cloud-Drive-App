import requests
from flask import request, json, jsonify
from memcache_app import webapp, memcache
from memcache_app.models import modify_tables
import sys

@webapp.route("/")
def main():
    return "hello from memcache server"

@webapp.route("/put", methods=['POST'])
def put():
    input = request.get_json() 
    key = input['key']
    value = input['value']
    ret = memcache.put(key, value)
    if ret:
        response = jsonify({"msg": 'SUCCESS'})
    else:
        response = jsonify({"msg": 'FULL'})
    return response

@webapp.route("/get", methods=['POST'])
def get():
    input = request.get_json() 
    key = input["key"]
    value = memcache.get(key)
    if value == -1:
        print("key missing", flush = True)
        return jsonify({"value": "MISS"})
    return jsonify({"value": value})

@webapp.route("/clear", methods=['GET', 'POST'])
def clear():
    memcache.clear()
    return jsonify({"msg": "Memcache has been cleared"}) 

@webapp.route("/config", methods=['POST'])
def config():
    input = request.get_json()
    capacity = rpolicy = None
    if input["capacity"]:
        capacity = int(input["capacity"])    
    if input["policy"]:
        rpolicy = int(input["policy"])
    ret = memcache.config(capacity, rpolicy)

    return "capacity = {}, replacement policy = {}".format(ret[0], ret[1])
    
@webapp.route("/keys")
def keys():
    return jsonify({"keys": memcache.keys()})

@webapp.route("/invalidate", methods=['POST'])
def invalidate():
    input = request.get_json() 
    memcache.invalidate(input["key"])
    return jsonify({"msg": "OK"})

@webapp.route("/refresh", methods=['GET', 'POST'])
def refresh():
    capacity, policy = modify_tables.get_config()
    ret = memcache.config(capacity, policy)
    capacity = str(ret[0] // (1024 * 1024))
    policy = 'LRU' if ret[1] else 'Random'
    msg = "current capacity: {}MB, replacement policy: {}".format(capacity, policy)
    print(msg, flush=True)
    return jsonify({"msg": msg})

@webapp.route("/statistics", methods=['GET', 'POST'])
def statistics():
    num, sz, requests, hit_rate, miss_rate = memcache.statistics()
    sz = str(format(sz / (1024 * 1024), '.3f')) + 'MB'
    return str(num) + ' ' + str(sz)