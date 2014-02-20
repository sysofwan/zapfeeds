from math import log
from datetime import datetime, timedelta

from app.util.time_util import epoch_seconds


def score(social_score, date):
    """The hot formula. date in datetime.datetime object"""
    social_score = max(1, social_score)
    order = log(social_score, 10)
    seconds = epoch_seconds(date) - 1134028003
    return round(order + seconds / 45000, 7)

def unweighted_score(social_score):
    social_score = max(1, social_score)
    order = log(social_score, 10)
    return round(order, 7)

def rank_content(content, weight=0.1):
    """
    @todo: improve algorithm long term
    """
    age = datetime.utcnow() - content.timestamp
    initial_social_shares = get_initial_social_shares(content)
    total_score = initial_social_shares + (content.predicted_shares * weight)
    if age < timedelta(days=3):
        return score(total_score, content.timestamp)
    else:
        return unweighted_score(total_score)


def get_initial_social_shares(content_obj):
    facebook_likes = content_obj.social_shares[0].facebook_shares
    retweets = content_obj.social_shares[0].retweets
    upvotes = content_obj.social_shares[0].upvotes
    return facebook_likes + retweets + upvotes