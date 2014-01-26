from algorithm import *


class Extract():
    def __init__(self, content_data):
        self.anchor = get_anchor_feature(content_data.soup)
        self.body = get_body_feature(content_data.soup)
        self.content_type = get_content_type_feature(content_data.type)
        self.description = get_description_feature(content_data.description)
        self.heading = get_heading_feature(content_data.html)
        self.html = get_html_feature(content_data.html)
        self.icon = get_icon_feature(content_data.icon_url)
        self.thumbnail = get_thumbnail_feature(content_data.image_url)
        self.timestamp = get_timestamp_feature(content_data.timestamp)
        self.title = get_title_feature(content_data.title)
        self.url = get_url_feature(content_data.url)
        temp_data = self.data_for_ratio()
        self.ratio = get_ratio_feature(temp_data)

    def data_for_ratio(self):
        data_dict = dict(self.body.items() +
                         self.title.items() +
                         self.description.items() +
                         self.html.items())
        return data_dict

    def aggregate_feature(self):
        raw_features = self.__dict__
        features = {}
        for feature in raw_features:
            features = dict(features.items() + raw_features[feature].keys())
        return features

    @staticmethod
    def arrange_feature(features):
        arranged = []
        keys = sorted(features.keys())
        for key in keys:
            arranged.append(features[key])

        return arranged

    def get_feature(self):
        features = self.aggregate_feature()
        return self.arrange_feature(features)
