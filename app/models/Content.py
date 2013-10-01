from app import db
from time import mktime
from datetime import datetime, timedelta
from contentMeta import ContentType, SiteName, Tag

class Content(db.Model):
	"""All contents indexed..."""
	__tablename__ = 'contents'

	id = db.Column(db.Integer, primary_key = True)
	url = db.Column(db.String(2048), unique=True, nullable=False)
	raw_url = db.Column(db.String(2048), unique=True, nullable=False)
	text = db.Column(db.String(100000))
	title = db.Column(db.String(1000), index=True, nullable=False)
	raw_html = db.Column(db.String())
	# convert to UTC before using
	timestamp = db.Column(db.DateTime(), nullable=False)
	description = db.Column(db.String(20000))
	image_url = db.Column(db.String(2048))
	rank = db.Column(db.Integer, index = True)
	meta_tags = db.Column(db.String())
	icon_url = db.Column(db.String(2048))

	type_id = db.Column(db.Integer, db.ForeignKey('content_types.id'), index = True)
	site_name_id = db.Column(db.Integer, db.ForeignKey('site_names.id'), index = True)
	content_source_id = db.Column(db.Integer, db.ForeignKey('content_sources.id'), index = True)

	socialShares = db.relationship('SocialShare', backref = 'content')

	@classmethod
	def getOrCreateContent(cls, session, **kargs):

		content = cls.getContentByLink(kargs['url'])
		if content:
			session.commit()
			return content

		content = cls(url = kargs['url'], title=kargs['title'], raw_url=kargs['raw_url'],
			timestamp=datetime.fromtimestamp(mktime(kargs['timestamp'])))

		if 'description' in kargs:
			content.description = kargs['description'] 
		if 'raw_html' in kargs:
			content.raw_html = kargs['raw_html']
		if 'content_type' in kargs:
			contentType = ContentType.getContentType(session, kargs['content_type'])
			if contentType:
				content.type = contentType
		if 'site_name' in kargs:
			siteName = SiteName.getOrCreateSiteName(session, kargs['site_name'])
			content.siteName = siteName
		if 'image_url' in kargs:
			content.image_url = kargs['image_url']
		if 'text' in kargs:
			content.text = kargs['text']
		if 'meta_tags' in kargs:
			content.meta_tags = kargs['meta_tags']
		if 'icon_url' in kargs:
			content.icon_url = kargs['icon_url']
		if 'tags' in kargs:
			tagObjects = []
			for tag in kargs['tags']:
				tagObjects.append(Tag.getOrCreateTag(session, tag))
			content.tags = tagObjects

		session.add(content)
		session.commit()
		return content

	@classmethod
	def getContentByLink(cls, url):
		return cls.query.filter(cls.url == url).first()

	@classmethod
	def getContentByRawUrl(cls, url):
		return cls.query.filter(cls.raw_url == url).first()

	@classmethod
	def getContentFromNDaysAgo(cls, daysAgo):
		return cls.query.filter(cls.timestamp > datetime.utcnow()-timedelta(days = daysAgo))

	@classmethod
	def getFrontPage(cls):
		return cls.query.order_by(cls.timestamp.desc())[0:32]

	@classmethod
	def getFrontPageVideos(cls, session):
		return session.query(Content, ContentType).filter(ContentType.type_string == 'video')\
				.filter(Content.type_id == ContentType.id).order_by(Content.timestamp.desc())[0:30]

	@classmethod
	def getFrontPageArticles(cls, session):
		return session.query(Content, ContentType).filter(ContentType.type_string == 'article')\
				.filter(Content.type_id == ContentType.id).order_by(Content.timestamp.desc())[0:30]		

	def getFriendlyDescription(self):
		"""Returns the description, truncated to 300 characters"""
		if (len(self.title) > 65):
			return self.description[:120] + '...'
		return self.description[:200] + '...' if len(self.description) > 200 else self.description





