import imp
from multiprocessing.sharedctypes import Value
import os
import base64
from urllib import response
import requests
import boto3

from flask import render_template, redirect, url_for, request, jsonify

from app import webapp
from app.models import modify_tables
# from app import ip_addr
from app import s3_client
from app import reko_client

@webapp.route('/api/textract/form',methods=['GET'])

def textract_form():
    return render_template("textract_form.html")


@webapp.route('/api/textract',methods=['POST'])

def textract_image():

    photo_name = request.form.get("key")

    if photo_name == "":
        return render_template("returnPage.html", content="Please input a key!")

    addr = modify_tables.search_photo(photo_name)
    if addr == "":
        return render_template("returnPage.html", content="No photo found!")

    response=reko_client.detect_text(Image={'S3Object':{'Bucket':webapp.config["BUCKET_NAME"],'Name':addr}})
    textDetections = []
    for text in response['TextDetections']:
        if text['Type'] == "LINE":
            textDetections.append(text['DetectedText'])

    if not textDetections:
        textDetections.append("No text detected!")

    data = s3_client.get_object(Bucket=webapp.config["BUCKET_NAME"], Key=addr)
    image = data.get('Body').read()
    image_base64 = str(base64.b64encode(image), encoding='utf-8')

    return render_template("returnText.html", name=photo_name, content=image_base64, text=textDetections)



@webapp.route('/api/celebrity/form',methods=['GET'])

def celebrity_form():
    return render_template("celebrity_form.html")


@webapp.route('/api/celebrity',methods=['POST'])

def celebrity_image():

    photo_name = request.form.get("key")

    if photo_name == "":
        return render_template("returnPage.html", content="Please input a key!")

    addr = modify_tables.search_photo(photo_name)
    if addr == "":
        return render_template("returnPage.html", content="No photo found!")

    response=reko_client.recognize_celebrities(Image={'S3Object':{'Bucket':webapp.config["BUCKET_NAME"],'Name':addr}})
    celebrityDetections = []
    for celebrity in response['CelebrityFaces']:
        celebrityDetections.append(celebrity['Name'])

    if not celebrityDetections:
        celebrityDetections.append("No celebrity detected!")

    data = s3_client.get_object(Bucket=webapp.config["BUCKET_NAME"], Key=addr)
    image = data.get('Body').read()
    image_base64 = str(base64.b64encode(image), encoding='utf-8')

    return render_template("returnCele.html", name=photo_name, content=image_base64, celebrity=celebrityDetections)



@webapp.route('/api/facial/form',methods=['GET'])

def facial_form():
    return render_template("facial_form.html")


@webapp.route('/api/facial',methods=['POST'])

def facial_image():

    photo_name = request.form.get("key")

    if photo_name == "":
        return render_template("returnPage.html", content="Please input a key!")

    addr = modify_tables.search_photo(photo_name)
    if addr == "":
        return render_template("returnPage.html", content="No photo found!")

    response=reko_client.detect_faces(Image={'S3Object':{'Bucket':webapp.config["BUCKET_NAME"],'Name':addr}}, Attributes=['ALL'])
    faceDetections = []
    for face in response['FaceDetails']:
        faceDetections.append('Between ' + str(face['AgeRange']['Low'])
              + ' and ' + str(face['AgeRange']['High']) + ' years old')
        faceDetections.append(" " + str(face['Gender']['Value']))
        faceDetections.append(" " + str(face['Emotions'][0]['Type']))

    

    data = s3_client.get_object(Bucket=webapp.config["BUCKET_NAME"], Key=addr)
    image = data.get('Body').read()
    image_base64 = str(base64.b64encode(image), encoding='utf-8')

    if not faceDetections:
        faceDetections.append("No face detected!")
        return render_template("returnPage.html", content=faceDetections[0])

    return render_template("returnFacial.html", name=photo_name, gender=faceDetections[1], age=faceDetections[0], emotion=faceDetections[2], content=image_base64)