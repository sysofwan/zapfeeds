import feedparser
import requests
import time
from bs4 import BeautifulSoup
import json
from app import db
from app.models.Content import Content
from apscheduler.scheduler import Scheduler
from urlparse import urlparse
from boilerpipe.extract import Extractor
import pickle
from tagger import Reader,Stemmer,Rater,Tagger
import unicodedata


sched = Scheduler()

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


def social_count(url,reddit=True):	
	data = {'facebook_shares':0,'retweets':0}

	#get facebooks share

	try:
		fb_temp = requests.get('https://graph.facebook.com/?ids='+url).json()
		data['facebook_shares'] = fb_temp[url]['shares']
	except KeyError:
		fb_temp = requests.get('https://graph.facebook.com/'+url).json()
		if 'shares' in fb_temp:
			data['facebook_shares'] = fb_temp['shares']
	except:
		pass
		
	#get twitters retweet
	twit_temp = requests.get('http://urls.api.twitter.com/1/urls/count.json?url='+url).json()
	if 'count' in twit_temp:
		data['retweets'] = twit_temp['count']
	
	#if reddits upvote data is not required, return data
	if reddit == False:
		return data
	
	data['upvotes'] = 0

	#get reddits upvote
	try:
		redditRedirectReq = requests.get('http://www.reddit.com/'+url)
		reddit_url = redditRedirectReq.url
		if reddit_url[-1] != '/':
			reddit_url += '/'
		reddit_url += '.json'
		reddit_temp = requests.get(reddit_url).json()
		data['upvotes'] = reddit_temp[0]['data']['children'][0]['data']['ups']
	except:
	      	pass

	return data

def url_content(url_primary,url_secondary=''):
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
	title_data1 = soup.find('meta',{'property':'og:title'})
	title_data2 = soup.find('meta',{'name':'title'})
	title_data3 = soup.find('meta',{'name':'twitter:title'})
	title_data4 = soup.find('h2',{'id':'image-title'})
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
	if title: data['title']=title
		
        #find description
       	desc = ''
       	desc_data1 = soup.find('meta',{'property':'og:description'})
       	desc_data2 = soup.find('meta',{'name':'description'})
       	desc_data3 = soup.find('meta',{'name':'twitter:description'})
	if 'imgur.com' in url:
		pass
       	elif desc_data1:
       		desc = desc_data1.get('content')
       	elif desc_data2:
       		desc = desc_data2.get('content')
       	elif desc_data3:
       		desc = desc_data3.get('content')
	if desc: data['description']=desc
			
        #find type
	type_doc = ''
	type_data1 = soup.find('meta',{'property':'og:type'})
	type_data2 = ''
	type_data2_temp = pageReq.headers
	if 'content-type' in type_data2_temp: type_data2=type_data2_temp['content-type']
	if 'imgur.com' in url:
		type_doc = 'image'
	elif type_data1:
		type_doc = type_data1.get('content')
	elif type_data2:
		type_doc = type_data2
		if 'image' in type_data2: type_doc = 'image'
	if type_doc: data['type']=type_doc
    
	
        #find keywords
	data['tags'] = []
	keywords = ''
	keyword_data1 = soup.find('meta',{'name':'keywords'})
	keyword_data2 = soup.find('meta',{'name':'news_keywords'})
	if keyword_data1:
		keywords = keyword_data1.get('content')
	elif keyword_data2:
		keywords = keyword_data2.get('content')
	if 'imgur.com' in url:
		keywords = ''
	if keywords: data['tags']=keywords.split(',')
	data['tags'] = list(set(data['tags'] + auto_tagger(pageReq.text)))
	
	#cleaning the data from tags.
	for tag in data['tags']:
		if '--' in tag:
			data['tags'].remove(tag)
		if len(tag) > 20:
			data['tags'].remove(tag)
	data['tags'] = [tag.replace('\'', '') for tag in data['tags']]
	data['tags'] = [tag.replace('\"', '') for tag in data['tags']]
	data['tags'] = [tag.strip() for tag in data['tags']]
		
    #find image_url
	image_url = ''
	image_data1 = soup.find('meta',{'property':'og:image'})
	image_data2 = soup.find('meta',{'name':'twitter:image'})
	image_data3 = soup.find('link',{'rel':'image_src'})
	if 'imgur.com' in url and image_data3:
		image_url = image_data3.get('href')
	elif image_data1:
		image_url = image_data1.get('content')
	elif image_data2:
		image_url = image_data2.get('content')
	if image_url: data['image_url']=image_url



	return data



def auto_tagger(raw_html):
	try:
		extractor = Extractor(extractor='ArticleExtractor', html=raw_html)
	except:
		print 'Problem extracting content for tagging'
		return []
	
	text_string = extractor.getText()
	text_string = unicodedata.normalize('NFKD', text_string).encode('ascii','ignore')

	try:
		tags = auto_tag(str(text_string),5)
	except:
		return []

	return [str(tag) for tag in tags]
	
	
def requestRssData(url, google=False, newsvine=False, fark=False):
	content = feedparser.parse(url)
	data = []
	for i in content.entries:
		dictData = {}
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
				url_primary = soup.find('span',{'class':'c-seed-source'}).a['href']
				url_secondary = ''
			except:
				print 'problem opening newsvine link'
				continue
		elif fark:
			dictData['title'] = dictData['title'].split('[')[0]
			try:
				soup = BeautifulSoup(requests.get(i.id).text)
				url_temp = soup.find('a',{'class':'outbound_link'})['href']
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

		#if content is in database, do not get page (url still needs to be in dict to allow socialCount)
		if Content.getContentByLink(url_primary):
			dictData['url'] = url_primary
		elif Content.getContentByLink(url_secondary):
			dictData['url'] = url_secondary
		else:
			#get the content if url is valid
			urlContentData = url_content(url_primary,url_secondary)
			if urlContentData:
				dictData = dict(dictData.items() + urlContentData.items())
			else:
				continue

		#get social count
		dictData = dict(dictData.items() + social_count(dictData['url']).items())

		data.append(dictData)
		time.sleep(1)
	return data


@sched.interval_schedule(hours=1)
def loadDatabase():

	for url in RSS+RSS_AGG:
		if 'google.com' in url:
			data = requestRssData(url,google=True)
		elif 'newsvine.com' in url:
			data = requestRssData(url,newsvine=True)
		elif 'feedsportal.com/c/35344/f' in url:
			data = requestRssData(url,fark=True)
		else:
			data = requestRssData(url)
		for content in data:
			print 'Storing ' + content['url'] + ' from ' + url + ' ...'
			Content.getOrCreateContent(db.session,**content)
		db.session.commit()

# accepts a html string and returns a soup object with only contents
def cleanSoupHtml(html):
	cleanHtml = html.replace('\n', '')
	cleanHtml = cleanHtml.replace('\\', '')
	soup = BeautifulSoup(cleanHtml, 'html5lib')
	return soup


