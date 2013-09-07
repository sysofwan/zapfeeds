from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import views
from models.Content import Content
from models.User import User
from models.contentMeta import Tag, TagContent, ContentType, SocialShare, SiteName