"""
-update word database for training machine learning algorithm based on likes
-part:
a)head (title+description)
b)body
c)url
-types:
a)word freq
b)topic
c)pos:
d)ner:
"""


import nltk
import rank_url
import time
import random
from algorithm import *
from social_data import get_total_shares
from app.background_services.aggregation.main import auto_tag


#==============================================================================
#==================================get data====================================
#==============================================================================


def get_title():
    title_list = []
    query = '''
            select
            title
            from
            contents
            '''
    data = query_database(query)
    for row in data:
        title_list.append(row[0])

    return title_list


def get_word_pos(pos_tag, tag_type):
    """
    @param pos_tag: tagged sentence
    @param tag_type: type of tag, 1.noun 2.verb

    @returns: list of word with tag_type
    """

    #determine type of tags
    if tag_type.lower() == 'noun':
        tag = 'NN'
    elif tag_type.lower() == 'verb':
        tag = 'VB'
    else:
        print 'Please choose a tag_type, "noun" or "verb" '
        return

    pos_list = []
    for elt in pos_tag:
        if tag in elt[1]:
            word = elt[0].lower()
            if word not in pos_list and word not in STOPWORD:
                pos_list.append(word)

    return pos_list


def get_head():
    """
    returns <title>,<description>,<social shares>
    """
    result = []
    query = '''
            select
            title, description, facebook_shares + retweets + upvotes
            from
            contents, social_shares
            where
            contents.id = social_shares.content_id
            '''
    data = query_database(query)
    for row in data:
        #place title if no description available
        if not row[1]:
            result.append([row[0] + ' ' + row[0], row[2]])
        else:
            result.append([row[0] + ' ' + row[1], row[2]])
    return result


def get_body(html=False):
    """
    parameters: html - extract text from html
    returns: <text><social shares>
    """
    result = []
    text = 'text'
    if html:
        text = 'raw_html'

    uniqid = query_database('select distinct id from contents')
    for id in uniqid:
        query = 'select ' + text + ',facebook_shares + retweets + upvotes '
        query += '''
                 from
                 contents, social_shares
                 where
                 contents.id = social_shares.content_id
                 '''
        query += 'and contents.id=' + str(id[0])
        data = query_database(query)
        if not data:
            continue
        else:
            raw_html = data[0][0]
            shares = data[0][1]
        if not raw_html and shares:
            continue
        if html:
            if raw_html and shares:
                result.append([html_to_text(raw_html), shares])
        else:
            result.append(raw_html, shares)
    return result


def get_url():
    """
    returns: 2D list with format:- <url1>,<social shares1>
    """
    query = '''
            select
            url, facebook_shares + retweets + upvotes
            from
            contents, social_shares
            where
            contents.id = social_shares.content_id;
            '''
    url_temp = query_database(query)
    url = [list(row) for row in url_temp]

    return url


#==============================================================================
#==================================semantic====================================
#==============================================================================


def transform_social_data(text_list, social_likes):
    """
    convert social_likes from 1D to 2D for scoring purpose
    checks equality of text list and social likes length
    """
    social_likes = [[i] for i in social_likes]
    if len(text_list) != len(social_likes):
        raise Exception('Length of text list and social list not equal')
    return social_likes


def scoring(tags, data_dict, count, social_likes=[]):
    """
    social_likes: measure tags weighted by social shares
    """
    weight = 1
    if social_likes:
        weight = social_likes[0]

    for tag in tags:
        if tag in data_dict:
            data_dict[tag] += weight
        else:
            data_dict[tag] = weight
        count += weight
        print 'insert tag: ', tag
        print 'count: ', data_dict[tag]
        print '\n\n--------------------'
    return data_dict, count


def get_topic(text, num_tags):
    if not text:
        return []

    tags = auto_tag(text, num_tags)
    tags_string = ' '.join([str(i) for i in tags])
    tags = tokenize(tags_string, stopword=True, punct=True,
                    lower=True, stem=True, single=True)

    #for tag in tags:
    #    print 'tag: ', tag

    return tags


def topic_stats(text_list, num_tags, social_likes=False, filename=''):
    """
    topic modelling frequency
    num_tags:
    - head 3
    - body 5
    """
    data = {}
    count = 0.0
    if social_likes:
        social_likes = transform_social_data(text_list, social_likes)

    for i in range(len(text_list)):
        tags = get_topic(text_list[i], num_tags)
        if not social_likes:
            data, count = scoring(tags, data, count)
        else:
            data, count = scoring(tags, data, count, social_likes=social_likes[i])

    if not count:
        raise Exception('denominator cannot be zero')
    #for tag in data:
    #    data[tag] /= count
    if filename:
        with open('data/topic/topic_' + filename + '.json', 'wb') as fp:
            json.dump(data, fp)
    return data


def get_keyword(text):
    if not text:
        return []
    token = tokenize(text, stopword=True, punct=True, lower=True, stem=True,
                     num=True, single=True, link=True)
    for i in token:
        print 'keyword: ', i
    return token


def keyword_stats(text_list, social_likes=False, filename=''):
    """
    word frequency
    what :calculate prob of each word occuring from the whole word corpus
    howto : for each content, sum(freq for each word * weight)
    """
    data = {}
    count = 0.0

    if social_likes:
        social_likes = transform_social_data(text_list, social_likes)

    for i in range(len(text_list)):
        token = get_keyword(text_list[i])
        if not social_likes:
            data, count = scoring(token, data, count)
        else:
            data, count = scoring(token, data, count, social_likes[i])

    if not count:
        raise Exception('denominator cannot be zero')
    #for word in data:
    #    data[word] /= count
    if filename:
        with open('data/keyword/keyword_' + filename + '.json', 'wb') as fp:
            json.dump(data, fp)
    return data


POS_NOUN = ['NN', 'NNS', 'NNP', 'NNPS']
POS_ADJ = ['JJ', 'JJR', 'JJS']
POS_VERB = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
POS_ADVERB = ['RB', 'RBR', 'RBS']
POS_WH = ['WDT', 'WP', 'WP$', 'WRB']
POS_WEIRD = ['UH', 'FW']


def get_pos(text, pos_tag):
    pos = []
    if not text:
        return pos
    token_text = tokenize(text)
    pos_text = nltk.pos_tag(token_text)
    for pair in pos_text:
        if len(pair) != 2:
            continue
        if pair[1] in pos_tag:
            word = pair[0]
            word = stemmer.stem(clean_front_end(word.lower()))
            if len(word) > 1:
                pos.append(word)
                print 'word pos: ', word
    return pos


def get_pos_tag(pos, pos_tag, social_likes):
    """
    helper function for pos_stats
    calculate popularity of each type pos_tag
    e.g list of popular noun, verb, etc
    todo:
    1. exclude urls
    """
    data = {}
    count = 0.0
    weight = []

    if social_likes:
        weight = social_likes[:]
    else:
        weight = [1] * len(pos)

    for i in range(len(pos)):
        for pair in pos[i]:
            word = ''
            if len(pair) != 2:
                print 'Data is not the correct length: ', pair
                continue
            if pair[1] in pos_tag:

                #clean word and stem
                word = pair[0].lower()
                word = stemmer.stem(clean_front_end(word))
                if is_link(word):
                    #print 'this is a link: ', word
                    continue
                    # exclude word with length < 1
                if len(word) <= 1:
                    continue

                # store result in data dict
                if word in data:
                    data[word] += weight[i]
                else:
                    data[word] = weight[i]
                count += weight[i]
                print '\n\n===========================\n'
                print 'word: ', word
                print 'count: ', data[word]

    if not count:
        return data
        #raise Exception('denominator cannot be zero')
    #for word in data:
    #    data[word] /= count
    return data


# takes forever to run!!!!!! mofo cunt
def pos_tagger(text_list):
    """
    2D list
    """
    print 'tokenizing data...'
    token_text = [tokenize(text) for text in text_list if text]

    print 'pos tagging data...'
    pos_text = [nltk.pos_tag(token) for token in token_text if token]

    return pos_text


def pos_stats(text_list, social_likes='', filename=''):
    """
    text_list: pre-tokenize, pre-pos_tag 2d list
    Measure if text contains popular nouns, verb, etc
    """
    data = {}
    #pos_text = pos_tagger(text_list)
    pos_text = text_list[:]

    print 'Extracting pos tags....'
    data['noun'] = get_pos_tag(pos_text, POS_NOUN, social_likes)
    data['verb'] = get_pos_tag(pos_text, POS_VERB, social_likes)
    data['adj'] = get_pos_tag(pos_text, POS_ADJ, social_likes)
    data['adverb'] = get_pos_tag(pos_text, POS_ADVERB, social_likes)
    data['wh'] = get_pos_tag(pos_text, POS_WH, social_likes)
    data['weird'] = get_pos_tag(pos_text, POS_WEIRD, social_likes)

    if filename:
        for tag in data:
            with open('data/pos/pos_' + tag + '_' + filename + '.json', 'wb') as fp:
                json.dump(data[tag], fp)
    return data, pos_text


NER_TAGS = ['LOCATION', 'ORGANIZATION', 'PERSON', 'FACILITY', 'GPE']


def get_ner(text, ner_tag):
    ner = []
    if not text:
        return ner
    token_text = tokenize(text)
    pos_text = nltk.pos_tag(token_text)
    ner_text = nltk.ne_chunk(pos_text)

    for pair in ner_text:
        if type(pair) != tuple:
            if pair.node in ner_tag:
                words = ' '.join([i[0] for i in pair])
                words = tokenize(words, stem=True, lower=True, stopword=True,
                                 punct=True)
                for word in words:
                    ner.append(word)
                    print 'ner word: ', word
    return ner


def get_ner_tag(text_list, entity, social_likes):
    """
    text_list: ner tagged 2d list
    """
    data = {}
    count = 0.0
    weight = []

    #print 'NER tagging data'
    #ner_list = [nltk.ne_chunk(pos) for pos in text_list]
    print type(text_list)
    print text_list
    ner_list = text_list[:]

    if social_likes:
        weight = social_likes[:]
    else:
        weight = [1] * len(text_list)

    for index in range(len(ner_list)):
        for pair in ner_list[index]:
            if type(pair) != tuple:
                if pair.node == entity:
                    words = ' '.join([i[0] for i in pair])
                    words = tokenize(words, stem=True, lower=True,
                                     stopword=True, punct=True)
                    for word in words:
                        if word in data:
                            data[word] += weight[index]
                        else:
                            data[word] = weight[index]
                        count += weight[index]
                        print '\n\n==========================='
                        print 'word: ', word
                        print 'count: ', data[word]

    if not count:
        return data
        #raise Exception('denominator cannot be zero')

    #for word in data:
    #    data[word] /= count
    return data


# takes forever to run!!!!!! mofo cunt
def ner_tagger(pos_list):
    print 'ner tagging data...'
    ner_list = [nltk.ne_chunk(i) for i in pos_list]

    return ner_list


def ner_stats(pos_list, social_likes='', filename=''):
    """
    text_list: pre-tokenize, pre-pos_tag 2d list
    Measure if text contains popular people, origanizations (NE)
    """
    data = {}
    ner_list = ner_tagger(pos_list)

    print 'extracting Named Entities...'
    for entity in NER_TAGS:
        data[entity] = get_ner_tag(ner_list, entity, social_likes)

    if filename:
        for tag in data:
            with open('data/ner/ner_' + tag.lower() + '_' + filename +
                      '.json', 'wb') as fp:
                json.dump(data[tag], fp)
    return data


#==============================================================================
#==================================url=========================================
#==============================================================================


def url_domain_like(domain_list, filename=False):
    url_dict = {}
    for url in domain_list:
        temp_dict = get_total_shares(url)
        url_dict[url] = sum([row[1] for row in temp_dict.items()])

    if filename:
        with open('data/url/domain_likes.json', 'wb') as fp:
            json.dump(url_dict, fp)

    return url_dict


def url_average_like(url_list, social_likes, filename=False):
    """
    parameters:
    - url_list: list of urls
    - social_likes: list of corresponding social likes to urls
    """
    data = {}
    urls = [link_to_domain(url) for url in url_list]
    for i in range(len(urls)):
        if urls[i] in data:
            data[urls[i]] += [social_likes[i]]
        else:
            data[urls[i]] = [social_likes[i]]
    for url in data:
        data[url] = sum(data[url]) / float(len(data[url]))

    if filename:
        with open('data/url/average_likes.json', 'wb') as fp:
            json.dump(data, fp)
    return data


def url_alexa(domain_list, filename=False):
    data = {}
    ranker = rank_url.AlexaTrafficRank()
    for domain in domain_list:
        try:
            data[domain] = ranker.get_rank(domain)
        except:
            print 'cannot find alexa rank for', domain
            continue
        print 'Domain: ', domain
        print 'Alexa rank: ', data[domain]
        time.sleep(random.uniform(1.0, 2.5))
    if filename:
        with open('data/url/alexa.json', 'wb') as fp:
            json.dump(data, fp)

    return data


def url_pagerank(domain_list, filename=False):
    data = {}
    ranker = rank_url.GooglePageRank()
    for domain in domain_list:
        try:
            data[domain] = ranker.get_rank(domain)
        except:
            print 'cannot find page rank for', domain
            continue
        print 'Domain: ', domain
        print 'Page rank: ', data[domain]
        time.sleep(random.uniform(1.0, 2.5))
    if filename:
        with open('data/url/pagerank.json', 'wb') as fp:
            json.dump(data, fp)

    return data


#==============================================================================
#==================================update db===================================
#==============================================================================


def update_freq(text_list, likes_list, filename=''):
    result = keyword_stats(text_list, social_likes=likes_list,
                           filename=filename)
    return


def update_topic(text_list, likes_list, filename=''):
    if 'head' in filename:
        num_tags = 3
    else:
        num_tags = 5
    result = topic_stats(text_list, num_tags, social_likes=likes_list,
                         filename=filename)
    return


def update_pos(pos_list, likes_list, filename=''):
    result = pos_stats(pos_list, social_likes=likes_list,
                       filename=filename)
    return


def update_ner(pos_list, likes_list, filename=''):
    result = ner_stats(pos_list, social_likes=likes_list,
                       filename=filename)
    return


def update_word_database():
    #get data
    print 'extracting header data...'
    head = get_head()
    head_text = []
    head_likes = []
    for row in head:
        head_text.append(row[0])
        head_likes.append(row[1])

    print 'extracting body data...'
    body = get_body(html=True)
    body_text = []
    body_likes = []
    for row in body:
        body_text.append(row[0])
        body_likes.append(row[1])

    #update each categories
    print 'updating header'
    filename = 'head'
    print 'frequency...'
    update_freq(head_text, head_likes, filename=filename)
    print 'topic...'
    update_topic(head_text, head_likes, filename=filename)
    print 'pos tagging data...'
    head_text_pos = pos_tagger(head_text)
    print 'pos...'
    update_pos(head_text_pos, head_likes, filename=filename)
    print 'ner...'
    update_ner(head_text_pos, head_likes, filename=filename)

    print 'updating body'
    filename = 'body'
    print 'frequency...'
    update_freq(body_text, body_likes, filename=filename)
    print 'topic...'
    update_topic(body_text, body_likes, filename=filename)
    print 'pos tagging data...'
    body_text_pos = pos_tagger(body_text)
    print 'pos...'
    update_pos(body_text_pos, body_likes, filename=filename)
    print 'ner...'
    update_ner(body_text_pos, body_likes, filename=filename)
    return


def update_url_database():
    print 'extracting url from database'
    url_social = get_url()
    domain_list = list(set([link_to_domain(row[0]) for row in url_social]))
    url = []
    social_likes = []
    for row in url_social:
        url.append(row[0])
        social_likes.append(row[1])

    print 'updating url average likes...'
    data = url_average_like(url, social_likes, filename=True)
    print 'updating domain likes...'
    data = url_domain_like(domain_list, filename=True)
    print 'updating url alexa...'
    data = url_alexa(domain_list, filename=True)
    print 'updating url pagerank...'
    data = url_pagerank(domain_list, filename=True)

    return


def update_aggregated_data():
    update_url_database()
    update_word_database()
    return