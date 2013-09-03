from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import views
from models.RankedContent import RankedContent
from models.User import User
from models.RawContent import RawContent
from models.Tag import Tag, TagsContents