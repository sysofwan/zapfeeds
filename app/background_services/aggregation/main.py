import unicodedata
import pickle
from datetime import datetime
from time import mktime

from app.models.Content import Content, Tag, SiteName, ContentType
from util import join_root_with_domain, get_og_property, get_meta_property, \
    get_twitter_property, clean_html, htmlParser
from app.background_services.aggregation.custom_url import get_raw_url
import feedparser
from bs4 import BeautifulSoup
from tagger import Reader, Stemmer, Rater, Tagger
from boilerpipe.extract import Extractor
from app.background_services import reqSession
import logging
from app.background_services.ranking.feature_extraction import Extract
import langid


logger = logging.getLogger(__name__)
weights = pickle.load(open('dict.pkl', 'rb'))
auto_tag = Tagger(Reader(), Stemmer(), Rater(weights))


class ContentData():
    """
    @TODO: check requests status code 200
    """

    def __init__(self, raw_url, feed):
        self.raw_url = raw_url
        self.feed = feed
        self.page_req = reqSession.get(raw_url)
        self.soup = BeautifulSoup(self.page_req.text, 'html5lib')
        self.url = get_url(self.page_req, self.soup)
        self.content_text = extract_article(self.page_req.text)
        self.title = get_title(self.soup, self.feed)
        self.description = get_description(self.soup, self.feed)
        self.timestamp = get_timestamp(self.feed)
        self.image_url = get_image_url(self.soup)
        self.icon_url = get_icon_url(self.soup, self.url)
        self.type = get_type(self.url, self.soup)
        self.raw_html = self.page_req.text

    def valid(self):
        return self.page_req.ok and not self.is_duplicate_url() and self.is_english()

    def is_duplicate_url(self):
        content = Content.get_content_by_link(self.url)
        if content:
            return True
        return False

    def is_english(self):
        text = self.content_text
        if not text:
            text = self.title
        language = langid.classify(text)
        return language[0] == 'en'


def get_primary_content_data(rss_url, source_id, session):
    """
    """
    feed_data = feedparser.parse(rss_url)
    for feed in feed_data.entries:
        if not is_duplicate_content(feed):
            try:
                content = get_content_from_feed(feed, source_id, session)

            except Exception as e:
                content = None
                logger.exception('Error parsing content with feed link: %s. RSS url: %s. Exception: %s, %s',
                                 feed.link, rss_url, e.__class__.__name__, e)

            if content:
                session.add(content)
                session.commit()


def get_content_from_feed(feed, source_id, session):
    """
    Return a content object from given feed
    Side effects:   Implicitly creates tag and site name database entry
                    if it does not exist
    """
    raw_url = get_raw_url(feed.link)
    content_data = ContentData(raw_url, feed)

    if not content_data.valid():
        return None

    return generate_content(content_data, source_id, session)


def generate_content(content_data, source_id, session):
    content = Content()
    content.url = content_data.url
    content.feed_id = get_feed_id(content_data.feed)
    content.title = content_data.title
    content.description = content_data.description
    content.image_url = content_data.image_url
    content.icon_url = content_data.icon_url
    content.timestamp = content_data.timestamp
    content.content_source_id = source_id

    content.tags = get_tags(content_data, session)
    content.site_name = get_site_name(content_data.soup, session)
    content.type = content_data.type

    features = Extract(content_data)
    content.feature_extraction = features.get_feature(convert_string=True)

    return content


def is_duplicate_content(feed):
    # TODO:  If there is still duplicate, we can check using raw title and domain
    feed_id = get_feed_id(feed)
    content = Content.get_content_by_feed_id(feed_id)
    if content:
        return True
    return False


def is_duplicate_url(url):
    content = Content.get_content_by_link(url)
    if content:
        return True
    return False


def get_feed_id(feed):
    try:
        feed_id = feed.id
    except:
        feed_id = feed.link
    return feed_id


def get_url(page_request, soup):
    url = get_og_property(soup, 'url')
    if not url or not url.startswith('http'):
        # throw out trailing id
        url = page_request.url.split('#')[0]
    return url


def get_title(soup, feed):
    og_title = get_og_property(soup, 'title')
    if og_title:
        return og_title
    tw_title = get_twitter_property(soup, 'title')
    if tw_title:
        return tw_title
    meta_title = get_meta_property(soup, 'title')
    if meta_title:
        return meta_title
    return clean_html(feed.title)


def get_description(soup, feed):
    og_desc = get_og_property(soup, 'description')
    if og_desc:
        return og_desc
    tw_desc = get_twitter_property(soup, 'description')
    if tw_desc:
        return tw_desc
    meta_desc = get_meta_property(soup, 'description')
    if meta_desc:
        return meta_desc
    return clean_html(feed.description)


def get_image_url(soup):
    og_image = get_og_property(soup, 'image')
    if og_image:
        return og_image
    tw_image = get_twitter_property(soup, 'image')
    if tw_image:
        return tw_image


def get_icon_url(soup, url):
    icon_node = soup.find('link', {'rel': 'icon'})
    if not icon_node:
        icon_node = soup.find('link', {'rel': 'shortcut icon'})
    if not icon_node:
        icon_node = soup.find('link', {'rel': 'Shortcut Icon'})
    return get_icon_url_from_node(icon_node, url)


def get_timestamp(feed):
    return datetime.fromtimestamp(mktime(feed.published_parsed))


def get_tags(content_data, session):
    """
    Returns tag objects from given soup.
    If tag is new, create it first (stores in db) and returns it.
    """
    tags = auto_tagger(content_data)
    tags_obj = []
    for tag in tags:
        tags_obj.append(Tag.get_or_create_tag(session, tag))
    return tags_obj


def clean_tags(tags):
    tags = [tag.replace('\'', '') for tag in tags]
    tags = [tag.replace('\"', '') for tag in tags]
    tags = [tag.strip() for tag in tags]
    return [tag for tag in tags if ('--' not in tag and 2 < len(tag) < 20)]


def auto_tagger(content_data):
    """
    @todo: find a better word corpus,
           experiment with different taggers
    """
    text = get_tagging_text(content_data)
    try:
        tags = auto_tag(text, 3)
    except Exception as e:
        logger.error('Error auto tagging data content id: %s. Exception: %s, %s',
                     content_data.id, e.__class__.__name__, e)
        return []
    return clean_tags([str(tag) for tag in tags])


def extract_article(html_text):
    try:
        extractor = Extractor(extractor='ArticleExtractor', html=html_text)
        text_string = extractor.getText()
        text_string = htmlParser.unescape(text_string)
    except Exception as e:
        logger.error('Error extracting article html: %s  \nException: %s, %s',
                     html_text, e.__class__.__name__, e)
        text_string = ''
    return text_string


def get_tagging_text(content_data):
    """
    @todo: exclude numbers,
           consider n-grams
    """
    title_text = content_data.title
    description_text = content_data.description
    body_text = content_data.content_text
    #increase weight for title and description
    text_string = [title_text] * 2 + [description_text] * 2 + [body_text]
    text_string = ' '.join(text_string)
    text_string = unicodedata.normalize('NFKD', text_string).encode('ascii', 'ignore')
    return str(text_string)


def get_site_name(soup, session):
    site_name = get_og_property(soup, 'site_name')
    if site_name:
        return SiteName.get_or_create_site_name(session, site_name)
    return None


def get_type(url, soup):
    if 'imgur.com' in url:
        type_str = 'image'
    else:
        type_str = get_og_property(soup, 'type')
    if type_str:
        type_str = type_str.split('.')[0]
        return ContentType.get_content_type(type_str)
    return None


def get_icon_url_from_node(icon_node, url):
    icon_url = '/favicon.ico'
    if icon_node and icon_node.get('href'):
        icon_url = icon_node.get('href')
    if icon_url.startswith('..'):
        icon_url = icon_url[2:]
    if icon_url[0] == '/' and icon_url[1] != '/':
        icon_url = join_root_with_domain(url, icon_url)
    return icon_url