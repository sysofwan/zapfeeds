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

def rank_content(content):
    age = datetime.utcnow() - content.timestamp
    social_share = content.social_shares[0]
    total_score = social_share.facebook_shares + social_share.retweets + social_share.upvotes
    if age < timedelta(days=3):
        return score(total_score, content.timestamp)
    else:
        return unweighted_score(total_score)