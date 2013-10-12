from math import log
from time_util import epoch_seconds


def score(social_score, date):
    """The hot formula. date in datetime.datetime object"""
    social_score = max(1, social_score)
    order = log(social_score, 10)
    seconds = epoch_seconds(date) - 1134028003
    return round(order + seconds / 45000, 7)