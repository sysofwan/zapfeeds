#!flask/bin/python
from app import app
from app.util.scheduled_jobs import sched

sched.start()
app.run(debug = True, host='0.0.0.0')