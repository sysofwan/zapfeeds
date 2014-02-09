#!flask/bin/python
# To kick off the script, run the following from the python directory:
#   PYTHONPATH=`pwd` python testdaemon.py start

import logging, time
from logging.handlers import RotatingFileHandler
from app.background_services.aggregation_jobs import update_contents

#third party libs
from daemon import runner
from datetime import timedelta


class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path = '/tmp/aggregate-daemon.pid'
        self.pidfile_timeout = 5

    def run(self):
        while True:
            logger.info('restarting aggregation...')
            start_time = time.time()
            try:
                update_contents()
            except Exception:
                logger.exception('UNCAUGHT EXCEPTION')
            logger.info('aggregation completed in %s', str(timedelta(seconds=time.time() - start_time)))
            time.sleep(600)


app = App()
logger = logging.getLogger()
logging.getLogger('requests').setLevel(logging.WARN)
logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler('aggregation.log', maxBytes=1000000)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

daemon_runner = runner.DaemonRunner(app)
#This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve = [file_handler.stream]
daemon_runner.do_action()