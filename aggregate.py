#!flask/bin/python
from app.background_services.aggregation_jobs import update_contents

import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger()
logging.getLogger('requests').setLevel(logging.WARN)
logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler('aggregation.log', maxBytes=3 * 1000000)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(logging.StreamHandler())

if __name__ == '__main__':
    logger.info('Starting aggregation process...')
    try:
        update_contents()
    except Exception as e:
        logger.exception('Caught exception: %s, %s', e.__class__.__name__, e)