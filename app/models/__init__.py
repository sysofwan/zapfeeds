from Content import Content
from app import app
import flask.ext.whooshalchemy as whooshalchemy

whooshalchemy.whoosh_index(app, Content)