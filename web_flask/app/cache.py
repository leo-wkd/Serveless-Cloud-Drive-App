'''
from dataclasses import replace
from flask import render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from uhashring import HashRing

from app import db
from app import webapp
# from app import ip_addr
from app.models import modify_tables
from app.models.create_tables import Cache
from app.models.create_tables import Statistics
import os
import requests

@webapp.route('/api/cache/form',methods=['GET'])

def cache_config_form():
    return render_template("config_form.html")

@webapp.route('/api/cache',methods=['POST'])

def cache_config():
    capacity = request.form.get("capacity", type=int)
    replace = request.form.get("replacement_policy")

    modify_tables.config(capacity, replace)
    response = requests.get(ip_addr + '/refresh')
    cache_response = response.json()

    return render_template("returnPage.html", content=cache_response["msg"])

@webapp.route('/api/cache/clear',methods=['POST'])
def cache_clear():
    response = requests.get(ip_addr + '/clear')
    cache_response = response.json()
    return render_template("returnPage.html", content=cache_response["msg"])

@webapp.route('/api/cache/stats',methods=['GET'])
def cache_stats():
    stats = modify_tables.query_stats()
    return render_template("stats.html", content=stats)
'''