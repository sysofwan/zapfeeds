import json
import numpy
import pickle
from sklearn import preprocessing


with open('data/algorithm.p', 'rb') as fs:
    algorithm = pickle.load(fs)


def predicted_shares(social_shares, content):
    features = get_complete_feature(social_shares, content)
    shares = get_predict_social_shares(features)
    return shares


def get_complete_feature(social_shares, content):
    social_shares_count = get_social_share_count(social_shares)
    incomplete_features = json.loads(content.feature_extraction)
    features = format_feature(incomplete_features, social_shares_count)
    return features


def get_social_share_count(social_shares):
    return social_shares.facebook_shares + \
           social_shares.twitter_rt + \
           social_shares.reddit_ups


def format_feature(feature_extraction, social_shares):
    features = feature_extraction + [social_shares]
    features = numpy.array(features)
    features = scale_feature(features)
    return features


def scale_feature(features):
    return preprocessing.scale(features)


def get_predict_social_shares(features):
    shares = 0
    shares = algorithm.predict(features)
    return shares
