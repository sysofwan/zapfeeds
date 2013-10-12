from apscheduler.scheduler import Scheduler
from get_data import requestRssData
from get_data_reddit import rss_data
from social_data import social_count
from app import db
from app.models.Content import Content
from app.models.contentMeta import SocialShare, ContentSource
from rank import score

sched = Scheduler()

@sched.interval_schedule(hours=1)
def load_database(force_refresh=False):
    sources = ContentSource.query.all()
    for source in sources:
        url = source.url
        if 'google.com' in url:
            data = requestRssData(url, google=True, force_refresh=force_refresh)
        elif 'newsvine.com' in url:
            data = requestRssData(url, newsvine=True, force_refresh=force_refresh)
        elif 'feedsportal.com/c/35344/f' in url:
            data = requestRssData(url, fark=True, force_refresh=force_refresh)
        elif 'reddit.com' in url:
            data = rss_data(url)
        else:
            data = requestRssData(url, force_refresh=force_refresh)
        for content in data:
            content['source_id'] = source.id
            print 'Storing ' + content['url'] + ' from ' + url + ' ...'
            Content.create_or_update_content(db.session, **content)
        db.session.commit()
    print 'done loading database...'


@sched.interval_schedule(hours=2)
def populate_social_shares():
    contents = Content.query.all()
    print contents[0]
    print "updating social shares"
    for i in contents:
        if i.get_shares_count() <= 3:
            data = social_count(i.url)
            social_share = SocialShare.createSocialShare(db.session, data['facebook_shares'], data['retweets'],
                                                        data['upvotes'])
            social_share.content = i
            db.session.commit()

        share_count = max([share.facebook_shares + share.retweets + share.upvotes for share in i.socialShares])
        i.rank = score(share_count, i.timestamp)
        db.session.commit()
