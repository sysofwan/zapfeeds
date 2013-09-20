#!flask/bin/python
from app import app
from app.util.get_data import sched

sched.start()
app.run(debug = True, host='0.0.0.0')