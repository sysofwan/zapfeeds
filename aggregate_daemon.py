#!flask/bin/python
import logging
from logging.handlers import RotatingFileHandler
from app.background_services.aggregation_jobs import update_contents


logger = logging.getLogger()
logging.getLogger('requests').setLevel(logging.WARN)
logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler('aggregation.log', maxBytes=1000000)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

import time
from datetime import timedelta

def run():
    while True:
        logger.info('restarting aggregation...')
        start_time = time.time()
        try:
            update_contents()
        except Exception:
            logger.exception('UNCAUGHT EXCEPTION')
        logger.info('aggregation completed in %s', str(timedelta(seconds=time.time() - start_time)))
        time.sleep(600)


if __name__ == "__main__":
    run()