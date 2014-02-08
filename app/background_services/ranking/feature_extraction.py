import json
from algorithm import *
from pprint import pprint


class Extract():
    """
    @todo: check num of features,
           deal with None data,
           testing
    """
    def __init__(self, content_data):
        self.anchor = get_anchor_feature(content_data=content_data.soup)
        self.body = get_body_feature(html_data=content_data.raw_html)
        self.content_type = get_content_type_feature(content_data=content_data.type)
        self.description = get_description_feature(content_data=content_data.description)
        self.heading = get_heading_feature(content_data=content_data.soup)
        self.html = get_html_feature(content_data=content_data.soup)
        self.icon = get_icon_feature(content_data=content_data.icon_url)
        self.thumbnail = get_thumbnail_feature(content_data=content_data.image_url)
        self.timestamp = get_timestamp_feature(content_data=content_data.timestamp)
        self.title = get_title_feature(content_data=content_data.title)
        self.url = get_url_feature(content_data=content_data.url)
        ratio_temp = self.ratio_data()
        self.ratio = get_ratio_feature(ratio_temp)

    def ratio_data(self):
        data_dict = dict(self.anchor.items() +
                         self.body.items() +
                         self.title.items() +
                         self.description.items() +
                         self.html.items())
        return data_dict

    def aggregate_feature(self):
        raw_features = self.__dict__
        features = {}
        for feature in raw_features:
            features = dict(features.items() + raw_features[feature].items())
        return features

    @staticmethod
    def arrange_feature(features):
        arranged = []
        keys = sorted(features.keys())
        #change arrangement to follow train_algorithm.py FEATURE
        for key in keys:
            arranged.append(features[key])

        return arranged

    def get_feature(self, convert_string=False):
        features = self.aggregate_feature()
        features = self.arrange_feature(features)
        if convert_string:
            features = json.dumps(features)
        return features



