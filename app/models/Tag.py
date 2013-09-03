from app import db

class Tag(db.Model):
	"""Tags for sorting content and responding to user preference"""
	__tablename__ = 'tags'

	id = db.Column(db.Integer, primary_key = True)
	tag_string = db.Column(db.String(64), index = True)

	rankedContents = db.relationship('RankedContent', backref = 'tags', secondary = 'tags_contents')
	primaryRankedContents = db.relationship('RankedContent', backref = 'primaryTag')

class TagsContents(db.Model):
	"""Many-to-many relationship between RankedContent and Tags"""
	__tablename__ = 'tags_contents'

	id = db.Column(db.Integer, primary_key = True)
	tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
	ranked_content_id = db.Column(db.Integer, db.ForeignKey('ranked_contents.id'))

