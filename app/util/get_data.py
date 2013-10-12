import feedparser
import requests
import time
from bs4 import BeautifulSoup
import json
from app.models.Content import Content
from urlparse import urlparse
from boilerpipe.extract import Extractor
import pickle
from tagger import Reader, Stemmer, Rater, Tagger
import unicodedata

RSS = ['http://rss.cnn.com/rss/cnn_topstories.rss',
       'http://feeds.gawker.com/lifehacker/full',
       'http://feeds.wired.com/wired/index',
       'http://feeds2.feedburner.com/time/topstories',
       'http://feeds.gawker.com/gizmodo/full',
       'http://www.theverge.com/rss/frontpage',
       'http://feeds.feedburner.com/TechCrunch/',
       'http://feeds.cbsnews.com/CBSNewsMain',
       'http://feeds.abcnews.com/abcnews/topstories',
       'http://feeds.reuters.com/reuters/MostRead',
       'http://feeds.bbci.co.uk/news/rss.xml',
       'http://feeds.nbcnews.com/feeds/topstories',
       'http://feeds.foxnews.com/foxnews/most-popular',
       'http://rssfeeds.usatoday.com/usatoday-NewsTopStories',
       'http://feeds.theguardian.com/theguardian/us/rss',
       'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
       'http://rss.nytimes.com/services/xml/rss/nyt/GlobalHome.xml',
       'http://www.npr.org/rss/rss.php?id=100',
       'http://www.npr.org/rss/rss.php?id=1001',
       'http://hosted2.ap.org/atom/APDEFAULT/3d281c11a96b4ad082fe88aa0db04305',
       'http://hosted2.ap.org/atom/APDEFAULT/386c25518f464186bf7a2ac026580ce7',
       'http://hosted2.ap.org/atom/APDEFAULT/cae69a7523db45408eeb2b3a98c0c9c5',
       'http://feeds.slate.com/slate',
       'http://feeds.people.com/people/headlines',
       'http://feeds.feedburner.com/DrudgeReportFeed',
       'http://feeds.huffingtonpost.com/HP/MostPopular',
       'http://feeds.huffingtonpost.com/huffingtonpost/raw_feed',
       'http://feeds.nationalgeographic.com/ng/News/News_Main',
       'http://www.washingtontimes.com/rss/headlines/news/headlines/',
       'http://feeds.washingtonpost.com/rss/world',
       'http://feeds.washingtonpost.com/rss/national']

RSS_AGG = ['http://digg.com/rss/top.rss',
           'http://news.yahoo.com/rss/',
           'https://news.google.com/news/feeds?output=rss&num=100',
           'http://rss.feedsportal.com/c/35344/f/661517/index.rss', #fark
           'http://www.newsvine.com/_feeds/rss2/index']

LEAVE_URL = ['www.youtube.com']


#set up tagger 
weights = pickle.load(open('dict.pkl', 'rb'))
auto_tag = Tagger(Reader(), Stemmer(), Rater(weights))


def url_content(url_primary, url_secondary=''):
    data = {}

    try:
        #modify imgur url
        if 'i.imgur.com' in url_primary:
            url_primary = url_primary[:url_primary.rfind('.')]

        #make the first request
        pageRequest = requests.get(url_primary)

        #clean url if from not domain name in LEAVE_URL
        if urlparse(pageRequest.url).netloc in LEAVE_URL:
            link = pageRequest.url
        else:
            #get the cleaner url
            link = pageRequest.url.split('?')[0]
            if len(link) > len(pageRequest.url.split('#')[0]):
                link = pageRequest.url.split('#')[0]

        # checks if page is available
        if pageRequest.status_code >= 400:
            if not url_secondary:
                print 'Page invalid'
                return data
            pageRequest = requests.get(url_secondary)
            link = pageRequest.url.split('?')[0]
            if pageRequest.status_code >= 400:
                print 'Unable to open url:' + url_secondary
                return data
    except:
        print 'Problem opening url in url_content: ', url_primary
        return data

    data['url'] = link
    data['raw_html'] = pageRequest.text

    #use beautiful soup to parse html
    soup = cleanSoupHtml(data['raw_html'])

    #array of meta tags
    metas = [i.attrs for i in soup('meta')]
    data['meta_tags'] = json.dumps(metas)

    #get metadatas and append to dict data
    if 'imgur.com' in data['url']:
        meta_data = get_metadata(url=data['url'])
    else:
        meta_data = get_metadata(pageReq=pageRequest)
    data = dict(data.items() + meta_data.items())

    return data


def get_metadata(url='', pageReq=''):
    '''
    REQUIRES: At least url or pageReq parameter provided
    MODIFIES: None
    EFFECTS : Returns a dictionary containing attributes; title, description,
              type, keywords and image_url if available
    TODO    : Check if soup has content or value attributes
    '''

    data = {}

    #check if enough parameters are passed
    if url:
        try:
            pageReq = requests.get(url)
            soup = BeautifulSoup(pageReq.text)
        except:
            #print error message
            print 'cannot open page in get metadata'
            return data
    elif pageReq:
        pass
    else:
        return data

    soup = BeautifulSoup(pageReq.text)

    #find title
    title = ''
    title_data1 = soup.find('meta', {'property': 'og:title'})
    title_data2 = soup.find('meta', {'name': 'title'})
    title_data3 = soup.find('meta', {'name': 'twitter:title'})
    title_data4 = soup.find('h2', {'id': 'image-title'})
    if title_data1:
        title = title_data1.get('content')
    elif title_data2:
        title = title_data2.get('content')
    elif title_data3:
        title = title_data3.get('content')
        if 'imgur.com' in url:
            title = title_data3.get('value')
    elif title_data4 and 'imgur.com' in url:
        title = title_data4.text
    if title: data['title'] = title

    #find description
    desc = ''
    desc_data1 = soup.find('meta', {'property': 'og:description'})
    desc_data2 = soup.find('meta', {'name': 'description'})
    desc_data3 = soup.find('meta', {'name': 'twitter:description'})
    if 'imgur.com' in url:
        pass
    elif desc_data1:
        desc = desc_data1.get('content')
    elif desc_data2:
        desc = desc_data2.get('content')
    elif desc_data3:
        desc = desc_data3.get('content')
    if desc: data['description'] = desc

    #find type
    type_doc = ''
    type_data1 = soup.find('meta', {'property': 'og:type'})
    type_data2 = ''
    type_data2_temp = pageReq.headers
    if 'content-type' in type_data2_temp:
        type_data2 = type_data2_temp['content-type']
    if 'imgur.com' in url:
        type_doc = 'image'
    elif type_data1:
        type_doc = type_data1.get('content').split('.')[0]
    elif type_data2:
        type_doc = type_data2
        if 'image' in type_data2: type_doc = 'image'
    if type_doc:
        data['content_type'] = type_doc


    #find keywords
    data['tags'] = []
    keywords = ''
    keyword_data1 = soup.find('meta', {'name': 'keywords'})
    keyword_data2 = soup.find('meta', {'name': 'news_keywords'})
    if keyword_data1:
        keywords = keyword_data1.get('content')
    elif keyword_data2:
        keywords = keyword_data2.get('content')
    if 'imgur.com' in url:
        keywords = ''
    if keywords: data['tags'] = keywords.split(',')
    data['tags'] = list(set(data['tags'] + auto_tagger(pageReq.text)))

    #cleaning the data from tags.
    data['tags'] = [tag.replace('\'', '') for tag in data['tags']]
    data['tags'] = [tag.replace('\"', '') for tag in data['tags']]
    data['tags'] = [tag.strip() for tag in data['tags']]
    data['tags'] = [tag for tag in data['tags'] if ( '--' not in tag and len(tag) < 20 and tag)]

    #find image_url
    image_url = ''
    image_data1 = soup.find('meta', {'property': 'og:image'})
    image_data2 = soup.find('meta', {'name': 'twitter:image'})
    image_data3 = soup.find('link', {'rel': 'image_src'})
    if 'imgur.com' in url and image_data3:
        image_url = image_data3.get('href')
    elif image_data1:
        image_url = image_data1.get('content')
    elif image_data2:
        image_url = image_data2.get('content')
    if image_url: data['image_url'] = image_url

    #find page icon
    icon_1 = soup.find('link', {'rel': 'icon'})
    icon_2 = soup.find('link', {'rel': 'shortcut icon'})
    icon_3 = soup.find('link', {'rel': 'Shortcut Icon'})
    if icon_1:
        data['icon_url'] = icon_1.get('href')
    elif icon_2:
        data['icon_url'] = icon_2.get('href')
    elif icon_3:
        data['icon_url'] = icon_3.get('href')

    #find site name
    site_name = soup.find('meta', {'property': 'og:site_name'})
    if site_name:
        data['site_name'] = site_name.get('content')

    return data


def auto_tagger(raw_html):
    try:
        extractor = Extractor(extractor='ArticleExtractor', html=raw_html)
    except:
        print 'Problem extracting content for tagging'
        return []

    text_string = extractor.getText()
    text_string = unicodedata.normalize('NFKD', text_string).encode('ascii', 'ignore')

    try:
        tags = auto_tag(str(text_string), 5)
    except:
        return []

    return [str(tag) for tag in tags]


def requestRssData(url, google=False, newsvine=False, fark=False, force_refresh=False):
    content = feedparser.parse(url)
    data = []
    for i in content.entries:
        dictData = {}
        if not force_refresh and Content.get_content_by_url(i.link):
            print 'content in database, continue..'
            continue
        dictData['raw_url'] = i.link
        dictData['description'] = cleanSoupHtml(i.description).get_text()
        dictData['title'] = i.title
        try:
            dictData['timestamp'] = i.published_parsed
        except:
            continue
        #check if rss from google news rss, clean url
        if google:
            url_primary = i.link.split('&url=')[1]
            url_secondary = ''
        elif newsvine:
            try:
                soup = BeautifulSoup(requests.get(i.link).text)
                url_primary = soup.find('span', {'class': 'c-seed-source'}).a['href']
                url_secondary = ''
            except:
                print 'problem opening newsvine link'
                continue
        elif fark:
            dictData['title'] = dictData['title'].split('[')[0]
            try:
                soup = BeautifulSoup(requests.get(i.id).text)
                url_temp = soup.find('a', {'class': 'outbound_link'})['href']
                url_primary = url_temp[url_temp.rfind('http'):]
                url_secondary = ''
            except:
                print 'problem opening fark link'
                continue
        else:
            try:
                url_primary = i.id
                url_secondary = i.link
            except AttributeError:
                url_primary = i.link
                url_secondary = ''
            except:
                continue

        #get the content if url is valid
        urlContentData = url_content(url_primary, url_secondary)
        if urlContentData:
            dictData = dict(dictData.items() + urlContentData.items())
        else:
            continue

        data.append(dictData)
        time.sleep(1)
    return data

# accepts a html string and returns a soup object with only contents
def cleanSoupHtml(html):
    cleanHtml = html.replace('\n', '')
    cleanHtml = cleanHtml.replace('\\', '')
    soup = BeautifulSoup(cleanHtml, 'html5lib')
    return soup


