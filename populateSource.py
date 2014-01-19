#!flask/bin/python
from app.models.contentMeta import ContentSource, ContentType
from app import db

sources = [
    {'url': 'http://rss.cnn.com/rss/cnn_topstories.rss', 'tag': 'news'},
    {'url': 'http://feeds.gawker.com/lifehacker/full', 'tag': 'blog'},
    {'url': 'http://feeds.wired.com/wired/index', 'tag': 'technology'},
    {'url': 'http://feeds2.feedburner.com/time/topstories', 'tag': 'news'},
    {'url': 'http://feeds.gawker.com/gizmodo/full', 'tag': 'technology'},
    {'url': 'http://www.theverge.com/rss/frontpage', 'tag': 'technology'},
    {'url': 'http://feeds.feedburner.com/TechCrunch/', 'tag': 'technology'},
    {'url': 'http://feeds.cbsnews.com/CBSNewsMain', 'tag': 'news'},
    {'url': 'http://feeds.abcnews.com/abcnews/topstories', 'tag': 'news'},
    {'url': 'http://feeds.reuters.com/reuters/MostRead', 'tag': 'news'},
    {'url': 'http://feeds.bbci.co.uk/news/rss.xml', 'tag': 'news'},
    {'url': 'http://feeds.nbcnews.com/feeds/topstories', 'tag': 'news'},
    {'url': 'http://feeds.foxnews.com/foxnews/most-popular', 'tag': 'news'},
    {'url': 'http://rssfeeds.usatoday.com/usatoday-NewsTopStories', 'tag': 'news'},
    {'url': 'http://feeds.theguardian.com/theguardian/us/rss', 'tag': 'news'},
    {'url': 'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml', 'tag': 'news'},
    {'url': 'http://rss.nytimes.com/services/xml/rss/nyt/GlobalHome.xml', 'tag': 'news'},
    {'url': 'http://www.npr.org/rss/rss.php?id=100', 'tag': 'news'},
    {'url': 'http://www.npr.org/rss/rss.php?id=1001', 'tag': 'news'},
    {'url': 'http://hosted2.ap.org/atom/APDEFAULT/3d281c11a96b4ad082fe88aa0db04305', 'tag': 'news'},
    {'url': 'http://hosted2.ap.org/atom/APDEFAULT/386c25518f464186bf7a2ac026580ce7', 'tag': 'news'},
    {'url': 'http://hosted2.ap.org/atom/APDEFAULT/cae69a7523db45408eeb2b3a98c0c9c5', 'tag': 'news'},
    {'url': 'http://feeds.slate.com/slate', 'tag': 'news'},
    {'url': 'http://feeds.people.com/people/headlines', 'tag': 'entertainment'},
    {'url': 'http://feeds.feedburner.com/DrudgeReportFeed', 'tag': 'news'},
    {'url': 'http://feeds.huffingtonpost.com/HP/MostPopular', 'tag': 'news'},
    {'url': 'http://feeds.huffingtonpost.com/huffingtonpost/raw_feed', 'tag': 'news'},
    {'url': 'http://feeds.nationalgeographic.com/ng/News/News_Main', 'tag': 'science'},
    {'url': 'http://www.washingtontimes.com/rss/headlines/news/headlines/', 'tag': 'news'},
    {'url': 'http://feeds.washingtonpost.com/rss/world', 'tag': 'news'},
    {'url': 'http://feeds.washingtonpost.com/rss/national', 'tag': 'news'},
    {'url': 'http://digg.com/rss/top.rss'},
    {'url': 'http://news.yahoo.com/rss/', 'tag': 'news'},
    {'url': 'https://news.google.com/news/feeds?output=rss&num=100', 'tag': 'news'},
    {'url': 'http://rss.feedsportal.com/c/35344/f/661517/index.rss', 'tag': 'news'},
    {'url': 'http://www.newsvine.com/_feeds/rss2/index', 'tag': 'news'},
    {'url': 'http://www.reddit.com/r/news/new/.rss?limit=100', 'tag': 'news'},
    {'url': 'http://www.reddit.com/r/worldnews/new/.rss?limit=100', 'tag': 'news'}
]

types = ['article', 'video', 'blog', 'website', 'book', 'music', 'image']


def populate_sources():
    for source in sources:
        if 'tag' in source:
            ContentSource.getOrCreateContentSource(db.session, source['url'], source['tag'])
        else:
            ContentSource.getOrCreateContentSource(db.session, source['url'])

    for type_name in types:
        ContentType.getOrCreateContentType(db.session, type_name)

if __name__ == '__main__':
    populate_sources()
    print 'Done populating sources'
    
    asdasdasdasd