#!venv/bin/python
from app import webapp as application

if __name__ == '__main__':
    webapp = application
    webapp.run('0.0.0.0',5002,debug=False)
