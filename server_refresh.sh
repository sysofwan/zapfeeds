#!/bin/sh
ssh apps@sayyidsofwan.com "cd aggregatordaddy;git pull;sudo -u apache ./killpython;DATABASE_URL=postgresql://apps@localhost/aggregator_daddy ./db_upgrade.py"
