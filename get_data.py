import feedparser
import urllib2
import json
import time


def data():
	content = feedparser.parse('http://rss.cnn.com/rss/cnn_topstories.rss')
	data = []
	for i in content.entries:
		link = i.id
		title = i.title
		desc = i.description
		pub = i.published
		html_content = urllib2.urlopen(link).read()
		fb = 0
		fb_temp = json.loads(urllib2.urlopen('https://graph.facebook.com/'+link).read())
		if 'shares' in fb_temp.keys():
			fb = fb_temp['shares']
		twit = 0
		twit_temp = json.loads(urllib2.urlopen('http://urls.api.twitter.com/1/urls/count.json?url='+link).read())
		if 'count' in twit_temp.keys():
			twit = twit_temp['count']
		reddit = 0
		#reddit_temp = json.loads(urllib2.urlopen(''+link+).read())
	
		data.append([link,title,desc,pub,html_content,fb,twit,reddit])
		time.sleep(1)
	return data
