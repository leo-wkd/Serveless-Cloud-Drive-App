from dataclasses import replace
from flask import render_template, redirect, url_for, request, jsonify

from app import webapp
from app.models import modify_tables
import os
import requests
from app import s3_client
from app import awscli

####################    Mem Cache Node  ##################
@webapp.route('/api/cache/clear_form',methods=['GET'])
def clear_cache_form():
    return render_template("clear.html")

@webapp.route('/api/cache/clear',methods=['GET', 'POST'])
def clear_cache():
    ip_list = modify_tables.get_ip()
    for ip_addr in ip_list:
        response = requests.get(ip_addr + '/clear')
    cache_response = response.json()
    return render_template("returnPage.html", content=cache_response["msg"])


####################    S3 and RDS   ##################
@webapp.route('/api/data/clear_form',methods=['Get'])
def data_clear_form():
    return render_template("delete.html")

@webapp.route('/api/data/clear',methods=['Get', 'POST'])
def delete_data():
    # delete info on database
    modify_tables.clear_photo()

    # delete images on S3
    response = s3_client.list_objects_v2(Bucket=webapp.config["BUCKET_NAME"], Prefix="images/")
    if response.get("Contents") is None:
        return render_template("returnPage.html", content="Actually no photo in system!")

    for object in response["Contents"]:
        s3_client.delete_object(Bucket=webapp.config["BUCKET_NAME"], Key=object["Key"])

    return render_template("returnPage.html", content="Successfully clear all photos!")
