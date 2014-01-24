from app.models.content_metadata import SocialShare
from app.background_services import reqSession

import logging

logger = logging.getLogger(__name__)

def get_social_share(url):
    social_share = SocialShare()
    social_share.facebook_shares = get_facebook_shares(url)
    social_share.retweets = get_twitter_retweets(url)
    social_share.upvotes = get_reddit_upvotes(url)
    return social_share

def get_total_shares(url):
    fb_shares = get_facebook_shares(url)
    twitter_rt = get_twitter_retweets(url)
    reddit_ups = get_reddit_upvotes(url)
    return fb_shares + twitter_rt + reddit_ups

def get_facebook_shares(url):
    try:
        fb_data = reqSession.get('https://graph.facebook.com/?ids='+url).json()
        return fb_data[url]['shares']
    except:
        fb_data = reqSession.get('https://graph.facebook.com/'+url).json()
        if 'shares' in fb_data:
            return fb_data['shares']
        return 0

def get_twitter_retweets(url):
    try:
        twitter_data = reqSession.get('http://urls.api.twitter.com/1/urls/count.json?url='+url).json()
    except Exception as e:
        logger.error('Unable to get retweets for url: %s. Exception: %s, %s',
                     url, e.__class__.__name__, e.message)
        return 0
    if 'count' in twitter_data:
        return twitter_data['count']
    return 0

def get_reddit_upvotes(url):
    reddit_url = get_reddit_data_url(url)
    try:
        reddit_data = reqSession.get(reddit_url).json()
        return reddit_data[0]['data']['children'][0]['data']['ups']
    except:
        return 0


def get_reddit_data_url(url):
    reddit_redirect_req = reqSession.get('http://www.reddit.com/'+url)
    reddit_url = reddit_redirect_req.url
    if reddit_url[-1] != '/':
        reddit_url += '/'
    return reddit_url +'.json'