
import numpy
import pickle
import logging
from sklearn import preprocessing

logger = logging.getLogger(__name__)

with open('data/algorithm.p', 'rb') as fs:
    algorithm = pickle.load(fs)


def predicted_shares(social_shares, content):
    initial_shares = get_social_share_count(social_shares)
    try:
        features = get_complete_feature(initial_shares, content)
        shares = get_predict_social_shares(features, initial_shares)
    except Exception as e:
        logger.exception('\nError predicting shares, content.id: %s. Exception: %s, %s',
                         content.id, e.__class__.__name__, e)
        logger.exception('using initial shares as predicted shares...')
        shares = initial_shares
    return shares


def get_complete_feature(initial_shares, content):
    incomplete_features = content.get_feature_extraction()
    features = format_feature(incomplete_features, initial_shares)
    return features


def get_social_share_count(social_shares):
    return social_shares.facebook_shares + social_shares.retweets + social_shares.upvotes


def format_feature(feature_extraction, social_shares):
    feature_extraction.insert(108, social_shares)
    features = scale_feature(feature_extraction)
    features = numpy.array(features)
    return features


def scale_feature(features):
    return preprocessing.scale(features)


def get_predict_social_shares(features, initial_shares):
    shares = algorithm.predict(features)[0]
    if shares < 0:
        shares *= -1
    if shares < initial_shares:
        shares = initial_shares
    return shares
