#!flask/bin/python
from app.background_services.aggregation_jobs import update_contents

import logging

logger = logging.getLogger()
logging.getLogger('requests').setLevel(logging.WARN)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

if __name__ == '__main__':
    logger.info('starting aggregation...')
    try:
        update_contents()
    except Exception as e:
        logger.exception('Caught exception: %s, %s', e.__class__.__name__, e)