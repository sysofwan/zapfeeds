import csv
import numpy
from algorithm import *
from pprint import pprint
from pprint import pprint
from sklearn import preprocessing
from sklearn.cross_validation import KFold
from sklearn.metrics import mean_absolute_error
import random

FEATURE = ['target',
           'anchor_adj',
           'anchor_adverb',
           'anchor_alexa',
           'anchor_average_likes',
           'anchor_char_length',
           'anchor_depth',
           'anchor_domain_likes',
           'anchor_gpe',
           'anchor_keyword',
           'anchor_length',
           'anchor_location',
           'anchor_noun',
           'anchor_organization',
           'anchor_pagerank',
           'anchor_person',
           'anchor_polarity',
           'anchor_punctuation',
           'anchor_sentence_length',
           'anchor_subjectivity',
           'anchor_tld_score',
           'anchor_topic',
           'anchor_verb',
           'anchor_weird',
           'anchor_wh',
           'anchor_word_length',
           'body_adj',
           'body_adverb',
           'body_char_length',
           'body_gpe',
           'body_keyword',
           'body_location',
           'body_noun',
           'body_organization',
           'body_person',
           'body_polarity',
           'body_punctuation',
           'body_sentence_length',
           'body_subjectivity',
           'body_topic',
           'body_verb',
           'body_weird',
           'body_wh',
           'body_word_length',
           'content_type',
           'desc_adj',
           'desc_adverb',
           'desc_char_length',
           'desc_gpe',
           'desc_keyword',
           'desc_location',
           'desc_noun',
           'desc_organization',
           'desc_person',
           'desc_polarity',
           'desc_punctuation',
           'desc_sentence_length',
           'desc_subjectivity',
           'desc_topic',
           'desc_verb',
           'desc_weird',
           'desc_wh',
           'desc_word_length',
           'heading_adj',
           'heading_adverb',
           'heading_char_length',
           'heading_gpe',
           'heading_keyword',
           'heading_location',
           'heading_noun',
           'heading_organization',
           'heading_person',
           'heading_polarity',
           'heading_punctuation',
           'heading_sentence_length',
           'heading_subjectivity',
           'heading_topic',
           'heading_verb',
           'heading_weird',
           'heading_wh',
           'heading_word_length',
           'html_a',
           'html_embed',
           'html_h',
           'html_input',
           'html_layout',
           'html_meta',
           'html_num',
           'html_p',
           'html_script',
           'html_style',
           'icon',
           'ratio_a_html',
           'ratio_a_word',
           'ratio_char_word',
           'ratio_desc_word',
           'ratio_embed_html',
           'ratio_h_html',
           'ratio_input_html',
           'ratio_layout_html',
           'ratio_meta_html',
           'ratio_p_html',
           'ratio_punctuation_word',
           'ratio_script_html',
           'ratio_style_html',
           'ratio_title_word',
           'ratio_word_html',
           'ratio_word_sent',
           'shares_num',
           'thumbnail',
           'timestamp_day',
           'timestamp_hour',
           'title_adj',
           'title_adverb',
           'title_char_length',
           'title_gpe',
           'title_keyword',
           'title_location',
           'title_noun',
           'title_organization',
           'title_person',
           'title_polarity',
           'title_punctuation',
           'title_sentence_length',
           'title_subjectivity',
           'title_topic',
           'title_verb',
           'title_weird',
           'title_wh',
           'title_word_length',
           'url_adj',
           'url_adverb',
           'url_alexa',
           'url_average_likes',
           'url_char_length',
           'url_depth',
           'url_domain_likes',
           'url_gpe',
           'url_keyword',
           'url_length',
           'url_location',
           'url_noun',
           'url_organization',
           'url_pagerank',
           'url_person',
           'url_polarity',
           'url_punctuation',
           'url_sentence_length',
           'url_subjectivity',
           'url_tld_score',
           'url_topic',
           'url_verb',
           'url_weird',
           'url_wh',
           'url_word_length']


def extract_feature(content_id=0, content_data={}, train=False):
    """
    @param content_id: integer from database
    @param content_data:
    1. url
    2. title
    3. timestamp
    4. description
    5. social_shares
    6. thumbnail
    7. icon_url
    8. type_id
    9. raw_html
    x. target
    @param train: label data
    @returns: dict of features with the above keys
    """
    #extract data
    view = view_data(content_id=content_id,
                     content_data=content_data)
    access = access_data(content_id=content_id,
                         content_data=content_data)

    #get label data
    target = []
    if train:
        if content_id:
            target_value = get_target(content_id)
            if target_value is not None:
                target = [('target', target_value)]
        elif content_data and 'target' in content_data:
            target = [('target', content_data['target'])]
        else:
            raise Exception('No labels provided')

    #aggregate all the dict data
    result_temp = dict(view.items() +
                       access.items() +
                       target)

    ratio = get_ratio_feature(result_temp)

    result = dict(result_temp.items() + ratio.items())

    #print the results
    print '\n========================================================\n\n'

    if content_id:
        print 'Id: ', content_id, '\n'
    elif content_data:
        print 'Title: ', content_data['title']
        print 'Url: ', content_data['url'], '\n'
    pprint(result)

    return result


def id_from_database():
    query = '''
            select
            id
            from
            contents
            order by
            id asc
            '''

    data = query_database(query)
    ids = []
    for row in data:
        ids.append(row[0])
    return ids


CONTENT_TYPE = ['url', 'title', 'timestamp', 'description', 'thumbnail', 'icon_url', 'type_id', 'raw_html']


def get_content_from_id(content_id):
    query = '''
            select
            url, title, timestamp, description, image_url, icon_url, type_id, raw_html
            from
            contents
            where
            id=
            '''
    query += str(content_id)
    data = query_database(query)
    data_dict = {}
    for row in data:
        for index in range(len(CONTENT_TYPE)):
            data_dict[CONTENT_TYPE[index]] = row[index]

    return data_dict


def test_extract_feature_content_data(id_range=[]):
    if id_range:
        ids = id_range
    else:
        ids = id_from_database()
    data_list = []
    for elt in ids:
        data_dict = get_content_from_id(elt)
        temp_dict = extract_feature(content_data=data_dict)
        if len(temp_dict) == (len(FEATURE) - 2):
            data_list.append(temp_dict)

    return data_list


def test_extract_feature_content_id(id_range=[]):
    if id_range:
        ids = id_range
    else:
        ids = id_from_database()
    data_list = []
    for num in ids:
        temp_dict = extract_feature(content_id=num, train=True)
        data_temp = [temp_dict[feat] for feat in FEATURE]
        if len(data_temp) == len(FEATURE):
            data_list.append(data_temp)
    data_list.insert(0, FEATURE)

    return data_list


def test_algorithm(x, y, clf, cv_folds=4):
    score = []
    mse = []
    cv = KFold(len(y), n_folds=cv_folds)
    for train, target in cv:
        print '\ntraining algorithm...'
        clf.fit(x[train], y[train])
        score_temp = clf.score(x[target], y[target])
        mse_temp = mean_absolute_error(y[target], clf.predict(x[target]))
        print 'score: ', score_temp
        print 'mse: ', mse_temp
        score.append(score_temp)
        mse.append(mse_temp)
    print '\n============stats============\n'
    print 'score mean: ', numpy.mean(numpy.array(score))
    print 'score median: ', numpy.median(numpy.array(score))
    print 'mse mean: ', numpy.mean(numpy.array(mse))
    print 'mse median: ', numpy.median(numpy.array(mse))

    return


def load_csv_data(filename):
    with open('data/' + filename, 'rU') as fs:
        data = [row for row in csv.reader(fs)]

    header = data[0]
    body_data = [[eval(col) for col in row] for row in data[1:]]

    return [header] + body_data[:]


def data_to_array(data, scale_data=False):
    x = []
    y = []
    body_data = data[1:]
    for row in body_data:
        x.append(row[1:])
        y.append(row[0])

    x = numpy.array(x)
    y = numpy.array(y)

    if scale_data:
        x = preprocessing.scale(x)

    return x, y








