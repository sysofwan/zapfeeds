

class Extract():
    def __init__(self, content_data):
        anchor = get_anchor_feature(content_data.soup)
        body = get_body_feature(content_data.soup)
        content_type = get_content_type_feature(content_data.type)
        description = get_description_feature(content_data.description)
        heading = get_heading_feature(content_data.html)
        html = get_html_feature(content_data.html)
        icon = get_icon_feature(content_data.icon_url)
        thumbnail = get_thumbnail_feature(content_data.image_url)
        timestamp = get_timestamp_feature(content_data.timestamp)
        title = get_title_feature(content_data.title)
        url = get_url_feature(content_data.url)
        ratio = get_ratio_feature(body, html, title, description, anchor)

    def arrange_feature(self):
        features = []
        return features

    def get_feature(self, scale=False):
        features = self.arrange_feature()

        return features