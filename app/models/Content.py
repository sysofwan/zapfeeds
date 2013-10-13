from app import db
from time import mktime
from datetime import datetime, timedelta
from contentMeta import ContentType, SiteName, Tag


class Content(db.Model):
    """All contents indexed..."""
    __tablename__ = 'contents'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(2048), unique=True, nullable=False)
    raw_url = db.Column(db.String(2048), unique=True, nullable=False)
    text = db.Column(db.String(100000))
    title = db.Column(db.String(1000), index=True, nullable=False)
    raw_html = db.Column(db.String())
    # convert to UTC before using
    timestamp = db.Column(db.DateTime(), nullable=False)
    description = db.Column(db.String(20000))
    image_url = db.Column(db.String(2048))
    rank = db.Column(db.Integer, index=True)
    meta_tags = db.Column(db.String())
    icon_url = db.Column(db.String(2048))

    type_id = db.Column(db.Integer, db.ForeignKey('content_types.id'), index=True)
    site_name_id = db.Column(db.Integer, db.ForeignKey('site_names.id'), index=True)
    content_source_id = db.Column(db.Integer, db.ForeignKey('content_sources.id'), index=True)

    socialShares = db.relationship('SocialShare', backref='content')

    @classmethod
    def create_or_update_content(cls, session, **kargs):

        content = cls.get_content_by_link(kargs['url'])
        if not content:
            content = cls(url=kargs['url'], title=kargs['title'], raw_url=kargs['raw_url'],
                          content_source_id=kargs['source_id'],
                          timestamp=datetime.fromtimestamp(mktime(kargs['timestamp'])))

        if 'description' in kargs:
            content.description = kargs['description']
        if 'raw_html' in kargs:
            content.raw_html = kargs['raw_html']
        if 'content_type' in kargs:
            contentType = ContentType.getContentType(kargs['content_type'])
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
    def get_content_by_link(cls, url):
        return cls.query.filter(cls.url == url).first()

    @classmethod
    def get_content_by_url(cls, url):
        return cls.query.filter(cls.raw_url == url).first()

    @classmethod
    def getContentFromNDaysAgo(cls, daysAgo):
        return cls.query.filter(cls.timestamp > datetime.utcnow() - timedelta(days=daysAgo))

    @classmethod
    def get_front_page(cls):
        return cls.query.order_by(cls.rank.desc())[0:48]

    @classmethod
    def getFrontPageVideos(cls, session):
        return session.query(Content, ContentType).filter(ContentType.type_string == 'video') \
                   .filter(Content.type_id == ContentType.id).order_by(Content.timestamp.desc())[0:30]

    @classmethod
    def getFrontPageArticles(cls, session):
        return session.query(Content, ContentType).filter(ContentType.type_string == 'article') \
                   .filter(Content.type_id == ContentType.id).order_by(Content.timestamp.desc())[0:30]

    @classmethod
    def get_front_page_in_range(cls, start_idx, end_idx):
        return cls.query.filter(cls.rank != None).order_by(cls.rank.desc())[start_idx:end_idx]

    def getFriendlyDescription(self):
        """Returns the description, truncated to 300 characters"""
        if not self.description:
            return ''
        if (len(self.title) > 65):
            return self.description[:120] + '...'
        return self.description[:200] + '...' if len(self.description) > 200 else self.description

    def get_shares_count(self):
        return len(self.socialShares)

    @property
    def fp_serialize(self):
        '''Returns the object serialized as a dict for front page use'''
        serialized = {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'text': self.text,
            'timestamp': self.timestamp,
            'description': self.description,
            'icon_url': self.icon_url,
            'tags': [tag_str.tag_string for tag_str in self.tags],
            'primary_tag': self.source.tag.tag_string,
        }
        if self.type:
            serialized['type'] = self.type.type_string
        if self.siteName:
            serialized['site_name'] = self.siteName.site_name
        if self.image_url:
            serialized['image_url'] = self.image_url
        else:
            serialized['image_url'] = ""

        return serialized





