#!/bin/sh
DATABASE_URL="postgresql://apps@localhost/aggregator_daddy"
cd /home/apps/aggregatordaddy
./aggregate.py
exit 0