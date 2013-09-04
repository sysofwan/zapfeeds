from app import db

class RawContent(db.Model):
	"""Raw content taken from aggregation and social sites
	This table is used to populate the RankedContent table"""

	DATA_TYPE_NEWS = 1
	DATA_TYPE_SHORT_TEXT = 2
	DATA_TYPE_PICTURES = 3
	DATA_TYPE_VIDEOS = 4
	DATA_TYPE_OTHERS = 5

	__tablename__ = 'raw_contents'

	id = db.Column(db.Integer, primary_key = True)
	url = db.Column(db.String(2048))
	text = db.Column(db.String(2048))
	data_type = db.Column(db.SmallInteger, default = DATA_TYPE_OTHERS)
	timestamp = db.Column(db.DateTime(True))
	facebook_likes = db.Column(db.Integer)
	reddit_upvotes = db.Column(db.Integer)
	twitter_retweets = db.Column(db.Integer)
	image_url = db.Column(db.String(2048))

	rankedContent = db.relationship('RankedContent', uselist = False, backref = 'rawContent')
