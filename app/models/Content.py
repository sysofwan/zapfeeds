from app import db
from time import mktime
from datetime import datetime, timedelta
from content_metadata import ContentType, SiteName, Tag, TagContent
from sqlalchemy import and_, or_
import random

CONTENTS_PER_PAGE = 30
TOP_CONTENTS_TO_SHUFFLE = 100

class Content(db.Model):
    """All contents indexed..."""
    __tablename__ = 'contents'
    __searchable__ = ['title']

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(2048), unique=True, nullable=False)
    feed_id = db.Column(db.String(2048), unique=True, nullable=False)
    title = db.Column(db.String(1000), index=True, nullable=False)
    # convert to UTC before using
    timestamp = db.Column(db.DateTime(), nullable=False)
    description = db.Column(db.String(20000))
    image_url = db.Column(db.String(2048))
    icon_url = db.Column(db.String(2048))

    rank = db.Column(db.Integer)
    predicted_shares = db.Column(db.Integer)
    real_shares = db.Column(db.Integer)

    type_id = db.Column(db.Integer, db.ForeignKey('content_types.id'), index=True)
    site_name_id = db.Column(db.Integer, db.ForeignKey('site_names.id'), index=True)
    content_source_id = db.Column(db.Integer, db.ForeignKey('content_sources.id'), index=True)

    social_shares = db.relationship('SocialShare', backref='content')

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
            contentType = ContentType.get_content_type(kargs['content_type'])
            if contentType:
                content.type = contentType
        if 'site_name' in kargs:
            siteName = SiteName.get_or_create_site_name(session, kargs['site_name'])
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
                tagObjects.append(Tag.get_or_create_tag(session, tag))
            content.tags = tagObjects

        session.add(content)
        session.commit()
        return content

    @classmethod
    def get_content_by_link(cls, url):
        return cls.query.filter(cls.url == url).first()

    @classmethod
    def get_content_by_feed_id(cls, feed_id):
        return cls.query.filter(cls.feed_id == feed_id).first()

    @classmethod
    def get_unranked_contents_by_age(cls, hours_ago):
        return cls.query.filter(
            and_(cls.rank == None, datetime.utcnow() - cls.timestamp >=
                                   timedelta(hours=hours_ago))).all()

    @classmethod
    def get_content_no_real_shares_by_age(cls, days_ago):
        return cls.query.filter(
            and_(cls.real_shares == None, datetime.utcnow() - cls.timestamp >=
                                   timedelta(days=days_ago))).all()

    @classmethod
    def get_content_for_ranking(cls, days):
        return cls.query.filter(and_(cls.social_shares != None,
                                     or_(cls.rank == None,
                                         and_(cls.social_shares != None,
                                              datetime.utcnow() - cls.timestamp <= timedelta(days=days))))).all()

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

    @classmethod
    def get_top_unviewed(cls, viewed=None):
        if not viewed:
            content = cls.query.filter(cls.rank != None)\
                          .order_by(cls.rank.desc())[0:TOP_CONTENTS_TO_SHUFFLE]
        else:
            content = cls.query.filter(and_(cls.rank != None, ~cls.id.in_(viewed)))\
                          .order_by(cls.rank.desc())[0:TOP_CONTENTS_TO_SHUFFLE]
        random.shuffle(content)
        return content[0:CONTENTS_PER_PAGE]


    @classmethod
    def get_top_by_pages(cls, page, viewed):
        return cls.query.filter(and_(cls.rank != None, ~cls.id.in_(viewed))).order_by(cls.rank.desc())\
            .paginate(page, CONTENTS_PER_PAGE, False).items

    @classmethod
    def get_top_tag_filtered(cls, page, tags, viewed=None):
        query = cls.query\
            .join(TagContent, Content.id == TagContent.content_id)\
            .join(Tag, Tag.id == TagContent.tag_id)
        if viewed:
            query = query.filter(and_(cls.rank != None, Tag.tag_string.in_(tags), ~cls.id.in_(viewed)))
        else:
            query = query.filter(and_(cls.rank != None, Tag.tag_string.in_(tags)))
        return query.order_by(cls.rank.desc()).paginate(page, CONTENTS_PER_PAGE, False).items


    @classmethod
    def get_top_type_filtered(cls, page, types, viewed=None):
        query = cls.query\
            .join(ContentType, ContentType.id == cls.type_id)
        if viewed:
            query = query.filter(and_(cls.rank != None, ContentType.type_string.in_(types), ~cls.id.in_(viewed)))
        else:
            query = query.filter(and_(cls.rank != None, ContentType.type_string.in_(types)))
        return query.order_by(cls.rank.desc()).paginate(page, CONTENTS_PER_PAGE, False).items

    @classmethod
    def get_top_for_query(cls, query, page):
        end_idx = page * CONTENTS_PER_PAGE
        start_idx = end_idx - CONTENTS_PER_PAGE
        contents = cls.search_title_for(query).order_by(cls.rank.desc())[start_idx:end_idx]
        return contents


    @classmethod
    def search_title_for(cls, query):
        return cls.query.whoosh_search(query)


    def getFriendlyDescription(self):
        """Returns the description, truncated to 300 characters"""
        if not self.description:
            return ''
        if len(self.title) > 65:
            return self.description[:120] + '...'
        return self.description[:200] + '...' if len(self.description) > 200 else self.description

    def get_shares_count(self):
        return len(self.social_shares)

    @property
    def fp_serialize(self):
        """Returns the object serialized as a dict for front page use"""
        serialized = {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'text': self.text,
            'timestamp': self.timestamp,
            'description': self.description,
            'icon_url': self.icon_url,
            'tags': [tag_str.tag_string for tag_str in self.tags],
        }
        if self.type:
            serialized['type'] = self.type.type_string
        if self.siteName:
            serialized['site_name'] = self.site_name.site_name
        if self.image_url:
            serialized['image_url'] = self.image_url
        else:
            serialized['image_url'] = ""

        if self.source.tag:
            serialized['primary_tag'] = self.source.tag.tag_string

        return serialized





