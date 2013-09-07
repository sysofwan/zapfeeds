import feedparser
import requests
import time
from bs4 import BeautifulSoup
from string import join
import json
from app import db
from app.models.Content import Content


def requestRssData(url):
	content = feedparser.parse(url)
	data = []
	for i in content.entries:
		dictData = {}
		link = i.id
		dictData['url'] = i.id
		dictData['title'] = i.title
		dictData['description'] = cleanSoupHtml(i.description).get_text()
		dictData['timestamp'] = i.published_parsed

		#request whole page
		dictData['raw_html'] = requests.get(link).text
		
		#request facebook shares
		dictData['facebook_shares'] = 0
		fb_temp = requests.get('https://graph.facebook.com/'+link).json()
		if 'shares' in fb_temp.keys():
			dictData['facebook_shares'] = fb_temp['shares']
		
		#request twitter retweets
		dictData['retweets'] = 0
		twit_temp = requests.get('http://urls.api.twitter.com/1/urls/count.json?url='+link).json()
		if 'count' in twit_temp.keys():
			dictData['retweets'] = twit_temp['count']

		# request reddit upvotes
		dictData['upvotes'] = 0
		try:
			redditRedirectReq = requests.get('http://www.reddit.com/'+link)
			reddit_url = redditRedirectReq.url
			if reddit_url[-1] == '/':
				reddit_url = reddit_url + '.json'
			else:
				reddit_url = reddit_url + '/.json'
			reddit_temp = requests.get(reddit_url).json()
			dictData['upvotes'] = reddit_temp[0]['data']['children'][0]['data']['ups']
		except:
			pass

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

def loadDatabse():
	rssFeeds = ['http://rss.cnn.com/rss/cnn_topstories.rss',
				'http://feeds.gawker.com/lifehacker/full',
				'http://feeds.wired.com/wired/index']
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


