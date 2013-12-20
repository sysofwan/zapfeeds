#!/usr/bin/python
import os, subprocess, sys
subprocess.call(['python', 'virtualenv.py', 'flask'])
if sys.platform == 'win32':
    bin = 'Scripts'
else:
    bin = 'bin'
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask<0.10'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'sqlalchemy==0.7.9'])
subprocess.call([os.path.join('flask', bin, 'pip'), 'install', 'flask-sqlalchemy'])
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
