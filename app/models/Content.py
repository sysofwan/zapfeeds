from app import db
from time import mktime
from datetime import datetime
from contentMeta import ContentType, SiteName, SocialShare, Tag

class Content(db.Model):
	"""All contents inndexed..."""
	__tablename__ = 'contents'

	id = db.Column(db.Integer, primary_key = True)
	url = db.Column(db.String(2048), unique=True, nullable=False)
	text = db.Column(db.String(100000))
	title = db.Column(db.String(1000), index=True, nullable=False)
	raw_html = db.Column(db.String())
	# convert to UTC before using
	timestamp = db.Column(db.DateTime(), nullable=False)
	description = db.Column(db.String(20000))
	image_url = db.Column(db.String(2048))
	rank = db.Column(db.Integer, index = True)
	meta_tags = db.Column(db.String())

	type_id = db.Column(db.Integer, db.ForeignKey('content_types.id'), index = True)
	site_name_id = db.Column(db.Integer, db.ForeignKey('site_names.id'), index = True)
	primary_tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), index = True)

	socialShares = db.relationship('SocialShare', backref = 'content')

	@classmethod
	def getOrCreateContent(cls, session, **kargs):
		socialShare = SocialShare.createSocialShare(session, kargs['facebook_shares'], 
			kargs['retweets'], kargs['upvotes'])

		content = cls.getContentByLink(session, kargs['url'])
		if content:
			socialShare.content = content
			return content

		content = cls(url = kargs['url'], title=kargs['title'], 
			timestamp=datetime.fromtimestamp(mktime(kargs['timestamp'])))
		socialShare.content = content

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
		if 'img_url' in kargs:
			content.image_url = kargs['img_url']
		if 'text' in kargs:
			content.text = kargs['text']
		if 'meta_tags' in kargs:
			content.meta_tags = kargs['meta_tags']
		if 'tags' in kargs:
			tagObjects = []
			for tag in kargs['tags']:
				tagObjects += Tag.getOrCreateTag(session, tag)
			content.tags = tagObjects

		session.add(content)
		session.commit()
		return content

	@classmethod
	def getContentByLink(cls, session, url):
		return session.query(cls).filter(cls.url == url).first()

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





