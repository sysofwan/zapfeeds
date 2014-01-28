#! /bin/sh
# -*- mode: python; coding: utf-8 -*-

# This file is used as both a shell script and as a Python script.

""":"
# This part is run by the shell.  It looks for an appropriate Python
# interpreter then uses it to re-exec this script.

if test -x /usr/bin/python2.7
then
  PYTHON=/usr/bin/python2.7
elif test -x /usr/local/bin/python2.7
then
  PYTHON=/usr/local/bin/python2.7
else
  echo 1>&2 "Python2.7 interpreter not found!"
  exit 1
fi

exec $PYTHON "$0" "$@"
" """

import os, subprocess, sys
subprocess.call(['python2.7', 'virtualenv.py', 'flask'])
if sys.platform == 'win32':
    bin = 'Scripts'
else:
    bin = 'bin'
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'sqlalchemy==0.7.9'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask-sqlalchemy'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'git+git://github.com/miguelgrinberg/Flask-WhooshAlchemy'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'sqlalchemy-migrate'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask-wtf'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'psycopg2'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'requests'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'stemming'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'tempita'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'html5lib'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'feedparser'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'beautifulsoup4'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'apscheduler'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'boilerpipe'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flup'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'tldextract'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'nltk'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', '-git+http://github.com/scipy/scipy/'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', '-U scikit-learn'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', '-U textblob'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'ftfy'])
