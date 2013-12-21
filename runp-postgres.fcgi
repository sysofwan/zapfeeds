#!flask/bin/python
import os
os.environ['DATABASE_URL'] = 'postgresql://apps@localhost/aggregator_daddy'

from flup.server.fcgi import WSGIServer
from app import app
from app.util.scheduled_jobs import sched

if __name__ == '__main__':
	sched.start()
    WSGIServer(app).run()
