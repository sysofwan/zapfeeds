from apscheduler.scheduler import Scheduler
from get_data import  RSS, RSS_AGG, requestRssData
from get_data_reddit import REDDIT_RSS, rss_data
from social_data import social_count
from app import db
from app.models.Content import Content
from app.models.contentMeta import SocialShare 

sched = Scheduler()

def loadDatabase():
	
	for url in RSS+RSS_AGG+REDDIT_RSS:
		if 'google.com' in url:
			data = requestRssData(url,google=True)
		elif 'newsvine.com' in url:
			data = requestRssData(url,newsvine=True)
		elif 'feedsportal.com/c/35344/f' in url:
			data = requestRssData(url,fark=True)
		elif 'reddit.com' in url:
			data = rss_data(url)
		else:
			data = requestRssData(url)
		for content in data:
			print 'Storing ' + content['url'] + ' from ' + url + ' ...'
			Content.getOrCreateContent(db.session,**content)
		db.session.commit()
	print 'done loading database...'

@sched.interval_schedule(minutes=30)
def populateSocialShares():
	contents = Content.getContentFromNDaysAgo(1)
	print "updating social shares"
	for i in contents:
		data = social_count(i.url)
		socialShare = SocialShare.createSocialShare(db.session, data['facebook_shares'], data['retweets'], data['upvotes'])
		socialShare.content = i
		db.session.commit()


print 'starting sequence...'
#loadDatabase()
populateSocialShares()
sched.start()
