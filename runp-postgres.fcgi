#!flask/bin/python
import os
os.environ['DATABASE_URL'] = 'postgresql://apps@localhost/aggregator_daddy'

from flup.server.fcgi import WSGIServer
from app import app
import logging
from logging.handlers import RotatingFileHandler

def init_logger():
    file_handler = RotatingFileHandler('app.log', maxBytes=3 * 1000000)
    file_handler.setLevel(logging.WARN)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    app.logger.addHandler(file_handler)
    logging.getLogger('sqlalchemy').addHandler(file_handler)


if __name__ == '__main__':
    init_logger()
    WSGIServer(app).run()
