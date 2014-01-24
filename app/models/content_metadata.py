from app import db
from datetime import datetime


class Tag(db.Model):
    """Tags for sorting content and responding to user preference"""
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    tag_string = db.Column(db.String(64), index=True, nullable=False, unique=True)

    contents = db.relationship('Content', backref='tags', secondary='tags_contents')
    contentSource = db.relationship('ContentSource', backref='tag')

    @classmethod
    def get_or_create_tag(cls, session, tagname):
        """Returns a tag with given tagname if it exists. Else, creates
        a new tag, add it to session and returns it"""
        tag = cls.get_tag(tagname)
        if tag:
            return tag
        tag = cls(tag_string=tagname)
        session.add(tag)
        session.commit()
        return tag

    @classmethod
    def get_tag(cls, tagname):
        return cls.query.filter(cls.tag_string == tagname).first()

    @classmethod
    def get_tags(cls, tags):
        return cls.query.filter(cls.tag_string.in_(tags)).all()

    @classmethod
    def get_all_tags(cls):
        return cls.query.order_by(cls.tag_string).all()


class TagContent(db.Model):
    """Many-to-many relationship between RankedContent and Tags"""
    __tablename__ = 'tags_contents'

    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    content_id = db.Column(db.Integer, db.ForeignKey('contents.id'))


class ContentType(db.Model):
    """Type  of content as defined in open graph"""
    __tablename__ = 'content_types'

    id = db.Column(db.Integer, primary_key=True)
    type_string = db.Column(db.String(64), index=True, nullable=False, unique=True)

    contents = db.relationship('Content', backref='type')

    @classmethod
    def get_or_create_content_type(cls, session, typename):
        """Returns ContentType with given type name if it exists. Else, creates
        a new ContentType, add it to session and returns it"""
        c_type = cls.get_content_type(typename)
        if c_type:
            return c_type
        c_type = cls(type_string=typename)
        session.add(c_type)
        session.commit()
        return c_type

    @classmethod
    def get_content_type(cls, typename):
        return cls.query.filter(cls.type_string == typename).first()

    @classmethod
    def get_content_types_with_contents(cls):
        return cls.query.filter(cls.contents != None).all()


class SocialShare(db.Model):
    """Number of shares/likes/upvotes in social sites"""
    __tablename__ = 'social_shares'

    id = db.Column(db.Integer, primary_key=True)
    facebook_shares = db.Column(db.Integer)
    retweets = db.Column(db.Integer)
    upvotes = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime(), nullable=False)

    content_id = db.Column(db.Integer, db.ForeignKey('contents.id'), nullable=False)

    def __init__(self, facebook_shares=0, retweets=0, upvotes=0):
        self.timestamp = datetime.utcnow()
        self.facebook_shares = facebook_shares
        self.retweets = retweets
        self.upvotes = upvotes

    @classmethod
    def createSocialShare(cls, session, facebbok, twitter, reddit):
        """creates a new social share, adds to session and returns it"""
        social = cls(facebook_shares=facebbok, retweets=twitter,
                     upvotes=reddit, timestamp=datetime.utcnow())
        session.add(social)
        return social


class SiteName(db.Model):
    """Name of content source site"""
    __tablename__ = 'site_names'

    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(128), index=True, nullable=False, unique=True)

    contents = db.relationship('Content', backref='site_name')

    @classmethod
    def get_or_create_site_name(cls, session, site_name):
        """Returns SiteName with given type name if it exists. Else, creates
        a new SiteName, add it to session and returns it"""
        s_name_obj = cls.get_site_name(site_name)
        if s_name_obj:
            return s_name_obj
        s_name_obj = cls(site_name=site_name)
        session.add(s_name_obj)
        session.commit()
        return s_name_obj

    @classmethod
    def get_site_name(cls, siteName):
        return cls.query.filter(cls.site_name == siteName).first()


class ContentSource(db.Model):
    """Stores RSS urls, reddit RSS, and other content sources"""
    __tablename__ = 'content_sources'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(2048), unique=True, nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))

    contents = db.relationship('Content', backref='source')

    @classmethod
    def get_or_create_content_source(cls, session, url, tag=None):
        cSource = cls.get_content_source(url)
        if cSource:
            return cSource
        cSource = cls(url=url)
        if tag:
            tag = Tag.get_or_create_tag(session, tag)
            cSource.tag = tag
        session.add(cSource)
        session.commit()
        return cSource

    @classmethod
    def get_content_source(cls, url):
        return cls.query.filter(cls.url == url).first()

    @classmethod
    def get_all_sources(cls):
        return cls.query.all()

