from flask import render_template
from app import webapp

@webapp.route('/',methods=['GET'])

def main():
    return render_template("base.html")