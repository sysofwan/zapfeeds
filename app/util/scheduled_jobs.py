from apscheduler.scheduler import Scheduler
from get_data import  RSS, RSS_AGG, requestRssData
from social_data import social_count
from app import db
from app.models.Content import Content
from app.models.contentMeta import SocialShare 

sched = Scheduler()

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

@sched.interval_schedule(hours=2)
def populateSocialShares():
	contents = Content.getContentFromNDaysAgo(1)
	print "updating social shares"
	for i in contents:
		if len(i.socialShares) > 3:
			continue
		data = social_count(i.url)
		socialShare = SocialShare.createSocialShare(db.session, data['facebook_shares'], data['retweets'], data['upvotes'])
		socialShare.content = i
		db.session.commit()