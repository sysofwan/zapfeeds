import feedparser
import requests
import time
from bs4 import BeautifulSoup
from string import join
import json
from app import db
from app.models.Content import Content
from apscheduler.scheduler import Scheduler

sched = Scheduler()

def requestRssData(url):
	content = feedparser.parse(url)
	data = []
	for i in content.entries:
		dictData = {}
		dictData['description'] = cleanSoupHtml(i.description).get_text()
		dictData['title'] = i.title
		dictData['timestamp'] = i.published_parsed

		link = i.id
		pageRequst = requests.get(link)

		# checks if page is available
		if pageRequst.status_code == 404:
			# if not, use rss link attr
			link = i.link
			pageRequst = requests.get(link)
			# Goto next loop if page is still not found
			if pageRequst.status_code == 404:
				continue

		if pageRequst.url != link:
			tempLink = link
			#	strips query parameters from url
			link = (pageRequst.url).split('?')[0]

		dictData['url'] = link
		# request whole page
		dictData['raw_html'] = pageRequst.text
		
		dictData['facebook_shares'] = getFacebookShares(link)
		dictData['retweets'] = getRetweets(link)
		dictData['upvotes'] = getUpvotes(link)

		#	if tempLink exists (we got redirected), check the link we came from
		if 'tempLink' in locals():
			dictData['facebook_shares'] += getFacebookShares(tempLink)
			dictData['retweets'] += getRetweets(tempLink)
			dictData['upvotes'] += getUpvotes(tempLink)

		#use beautiful soup to parse html
		soup = cleanSoupHtml(dictData['raw_html'])

		#array of meta tags
		metas = [i.attrs for i in soup('meta')]
		dictData['meta_tags'] = json.dumps(metas)

		for meta in metas:
			if 'property' in meta and 'content' in meta:
				metaProp = meta['property']
				metaContent = meta['content']
				if metaProp == 'og:type':
					dictData['content_type'] = metaContent
				elif metaProp == 'og:site_name':
					dictData['site_name'] = metaContent
				elif metaProp == 'og:image':
					dictData['img_url'] = metaContent

		paragraphs = [para.get_text() for para in soup('p')]
		dictData['text'] = join(paragraphs, '\n')
	
		data.append(dictData)
		time.sleep(0.5)
	return data

def getFacebookShares(url):
	fb_temp = requests.get('https://graph.facebook.com/'+url).json()
	if 'shares' in fb_temp:
		return fb_temp['shares']
	return 0

def getRetweets(url):
	twit_temp = requests.get('http://urls.api.twitter.com/1/urls/count.json?url='+url).json()
	if 'count' in twit_temp:
		return twit_temp['count']
	return 0

def getUpvotes(url):
	try:
		redditRedirectReq = requests.get('http://www.reddit.com/'+url)
		reddit_url = redditRedirectReq.url
		if reddit_url[-1] == '/':
			reddit_url = reddit_url + '.json'
		else:
			reddit_url = reddit_url + '/.json'
		reddit_temp = requests.get(reddit_url).json()
		return reddit_temp[0]['data']['children'][0]['data']['ups']
	except:
		return 0

@sched.interval_schedule(hours=1)
def loadDatabase():
	rssFeeds = ['http://rss.cnn.com/rss/cnn_topstories.rss',
<<<<<<< HEAD
				'http://feeds.gawker.com/lifehacker/full',
				'http://feeds.wired.com/wired/index',
				'http://feeds2.feedburner.com/time/topstories',
				'http://feeds.gawker.com/gizmodo/full',
				'http://www.theverge.com/rss/frontpage',
				'http://feeds.feedburner.com/TechCrunch/']
=======
			'http://feeds.wired.com/wired/index']
>>>>>>> c2d73ebf8a587eeb5e8a2eb75c64b9820ddccc76
	for url in rssFeeds:
		data = requestRssData(url)
		for content in data:
			Content.getOrCreateContent(db.session,**content)
		db.session.commit()

# accepts a html string and returns a soup object with only contents
def cleanSoupHtml(html):
	cleanHtml = html.replace('\n', '')
	cleanHtml = cleanHtml.replace('\\', '')
	soup = BeautifulSoup(cleanHtml, 'html5lib')

	#	follow same pattern for everything that we want removed
	[s.decompose() for s in soup('script')]
	[s.decompose() for s in soup('link')]
	[s.decompose() for s in soup('nav')]
	[s.decompose() for s in soup.find_all('div', 'nav')]
	[s.decompose() for s in soup.find_all(id='cnn_hdr')]
	[s.decompose() for s in soup.find_all('div', 'cnn_strybtntools')]
	[s.decompose() for s in soup.find_all('div', 'cnn_strycntntrgt')]
	[s.decompose() for s in soup.find_all('div', 'cnn_strylftcntnt')]
	[s.decompose() for s in soup.find_all('div', 'cnn_stryshrwdgtbtm')]

	return soup


