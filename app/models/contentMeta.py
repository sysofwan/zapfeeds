from app import db
from datetime import datetime

class Tag(db.Model):
	"""Tags for sorting content and responding to user preference"""
	__tablename__ = 'tags'

	id = db.Column(db.Integer, primary_key = True)
	tag_string = db.Column(db.String(64), index = True, nullable=False, unique=True)

	contents = db.relationship('Content', backref = 'tags', secondary = 'tags_contents')
	primaryContents = db.relationship('Content', backref = 'primaryTag')

	@classmethod
	def getOrCreateTag(cls, session, tagname):
		"""Returns a tag with given tagname if it exists. Else, creates 
		a new tag, add it to session and returns it"""
		tag = cls.getTag(session, tagname)
		if tag:
			return tag
		tag = cls(tag_string =  tagname)
		session.add(tag)
		return tag

	@classmethod
	def getTag(cls, session, tagname):
		return session.query(cls).filter(cls.tag_string == tagname).first()


class TagContent(db.Model):
	"""Many-to-many relationship between RankedContent and Tags"""
	__tablename__ = 'tags_contents'

	id = db.Column(db.Integer, primary_key = True)
	tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
	content_id = db.Column(db.Integer, db.ForeignKey('contents.id'))

class ContentType(db.Model):
	"""Type  of content as defined in open graph"""
	__tablename__ = 'content_types'

	id = db.Column(db.Integer, primary_key = True)
	type_string = db.Column(db.String(64), index = True, nullable=False, unique=True)

	contents = db.relationship('Content', backref = 'type')

	@classmethod
	def getOrCreateContentType(cls, session, typename):
		"""Returns ContentType with given type name if it exists. Else, creates 
		a new ContentType, add it to session and returns it"""
		cType = cls.getContentType(session, typename)
		if cType:
			return cType
		cType = cls(type_string =  typename)
		session.add(cType)
		session.commit()
		return cType

	@classmethod
	def getContentType(cls, session, typename):
		return session.query(cls).filter(cls.type_string == typename).first()

class SocialShare(db.Model):
	"""Number of shares/likes/upvotes in social sites"""
	__tablename__ = 'social_shares'

	id = db.Column(db.Integer, primary_key = True)
	facebook_shares = db.Column(db.Integer)
	retweets = db.Column(db.Integer)
	upvotes = db.Column(db.Integer)
	timestamp = db.Column(db.DateTime(), nullable=False)

	content_id = db.Column(db.Integer, db.ForeignKey('contents.id'))

	@classmethod
	def createSocialShare(cls, session, facebbok, twitter, reddit):
		"""creates a new social share, adds to session and returns it"""
		social = cls(facebook_shares = facebbok, retweets = twitter, 
			upvotes = reddit, timestamp = datetime.utcnow())
		session.add(social)
		return social


class SiteName(db.Model):
	"""Name of content source site"""
	__tablename__ = 'site_names'
	
	id = db.Column(db.Integer, primary_key = True)
	site_name = db.Column(db.String(64), index = True, nullable=False, unique=True)

	contents = db.relationship('Content', backref = 'siteName')

	@classmethod
	def getOrCreateSiteName(cls, session, siteName):
		"""Returns SiteName with given type name if it exists. Else, creates 
		a new SiteName, add it to session and returns it"""
		sName = cls.getSiteName(session, siteName)
		if sName:
			return sName
		sName = cls(site_name =  siteName)
		session.add(sName)
		session.commit()
		return sName

	@classmethod
	def getSiteName(cls, session, siteName):
		return session.query(cls).filter(cls.site_name == siteName).first()

