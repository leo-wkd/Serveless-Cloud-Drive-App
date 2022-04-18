import imp
from memcache_app import webapp as application

if __name__ == '__main__':
    webapp = application
    webapp.run('0.0.0.0', 5001, debug=False)
