from datetime import datetime
from math import log


epoch = datetime(1970, 1, 1)

def epoch_seconds(timestamp):
    """Returns the number of seconds from the epoch to date."""
    return (timestamp - epoch).total_seconds()

def score(social_score, date):
    """The hot formula. date in datetime.datetime object"""
    order = log(social_score, 10)
    seconds = epoch_seconds(date) - 1134028003
    return round(order + seconds / 45000, 7)