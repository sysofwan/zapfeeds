#!flask/bin/python
from app import app
from app.util.scheduled_jobs import sched

if __name__ == "__main__":
    sched.start()
    app.run(debug=True)
