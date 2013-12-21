#!/bin/sh
ssh apps@10.0.0.24 "cd aggregatordaddy;git pull;sudo -u apache ./killpython;DATABASE_URL=postgresql://apps@localhost/aggregator_daddy ./db_upgrade.py"