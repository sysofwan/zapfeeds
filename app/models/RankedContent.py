from app import db

class RankedContent(db.Model):
	"""Content taken fron RawContent and ranked."""
	__tablename__ = 'ranked_contents'

	id = db.Column(db.Integer, primary_key = True)
	raw_content_id = db.Column(db.Integer, db.ForeignKey('raw_contents.id'))
	title = db.Column(db.String(140), index = True)
	description = db.Column(db.String(4096))
	rank = db.Column(db.Integer, index = True)
	primary_tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), index = True)
