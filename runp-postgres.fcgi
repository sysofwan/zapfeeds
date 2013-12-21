#!flask/bin/python
import os
os.environ['DATABASE_URL'] = 'postgresql://apps@localhost/aggregator_daddy'

from flup.server.fcgi import WSGIServer
from app import app

if __name__ == '__main__':
    WSGIServer(app).run()
