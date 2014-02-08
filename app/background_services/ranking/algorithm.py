"""

"""

from app.models.Content import Content
from app.models.content_metadata import SocialShare
from boilerpipe.extract import Extractor
from bs4 import BeautifulSoup
import unicodedata
import string
import json
import tldextract
from pprint import pprint
import re
from textblob import TextBlob
from urlparse import urlparse
from nltk.corpus import stopwords
from nltk.tokenize.punkt import PunktWordTokenizer
from nltk.tokenize import TreebankWordTokenizer
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize


#==============================================================================
#                               global var
#==============================================================================

# stopwords in nltk
STOPWORD = stopwords.words('english')

# punctutations in string library
PUNCT = [i for i in string.punctuation]

#from nltk.stem.wordnet import WordNetLemmatizer
#lemmatizer = WordNetLemmatizer()

# stemmer from nltk library
stemmer = PorterStemmer()

# punctuations in a number
NUM_PUNCT = [' ', ',', '-', 'bn', 'pm', 'am', 's', 'm',
             'h', 'k', 'm', 'b']


# load list of top level domain
with open('data/TLD.txt', 'r') as fs:
    TLD = ['.' + i for i in fs.read().split('\r\n') if i]

# list of all protocols
PROTOCOL = ['http:', 'https:']

#==============================================================================
#                               general fn
#==============================================================================


def clean_front_end(text):
    result = text
    result = result.replace("\n", '')
    if not result:
        return ''
    while result[0] in PUNCT:
        result = result[0].replace(result[0], '') + result[1:]
        if not result:
            return ''
    while result[-1] in PUNCT:
        result = result[:-1] + result[-1].replace(result[-1], '')
        if not result:
            return ''
    result = result.replace("'s", '')
    result = result.strip()
    return result


def is_number(text):
    if text.isdigit():
        return float(text)
    if text[0].isdigit() or text[-1].isdigit():
        temp = text[:]
        for punct in NUM_PUNCT:
            temp = temp.replace(punct, '')
        if temp.isdigit():
            return float(temp)
        if temp.count('.') == 1 and (temp.replace('.', '')).isdigit():
            return float(temp)
    return False


def is_link(text):
    for char in TLD + PROTOCOL:
        if char in text:
            return True
    return False


def complete_url(a_link, url):
    if a_link[0] == '#':
        full_url = url + a_link
    elif a_link[0] == '/' or a_link[2] == '../':
        a_link = a_link[a_link.find('/'):]
        full_url = urlparse(url).netloc + a_link
    elif is_link(a_link):
        full_url = a_link
    else:
        url_temp = url[:url.rfind('/') + 1]
        full_url = url_temp + a_link

    return full_url


def link_to_domain(link, sub_domain=False):
    """
    @param sub_domain: includes the sub domain of the link
    """
    domain = ''
    if sub_domain:
        domain = urlparse(link).netloc
    else:
        domain_temp = tldextract.extract(link)
        if domain_temp.domain:
            domain = '.'.join(domain_temp[1:])

    return domain


def link_to_text(link):
    word_list = []
    try:
        paths = urlparse(link)[2]
    except:
        print 'cannot apply urlparse to given link'
    for path in paths.split('/'):
        if path:
            for word in path.split('-'):
                word_list.append(word.lower())
    words = ' '.join(word_list)

    return words


def open_json_file(filename):
    """
    open json file
    """
    with open(filename, 'rb') as fs:
        data = json.load(fs)
    return data


def html_to_text(html):
    try:
        extractor = Extractor(extractor='ArticleExtractor', html=html)
    except:
        print 'problem extracting text from html'
        return ''
    text = extractor.getText()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    return text


def tokenize(text, stopword=False, punct=False, lower=False,
             stem=False, num=False, single=False, link=False):
    """
    num: True, exclude numbers
    single: True, exclude single char
    todo: deal with unicode mafuckers
    """
    token = []
    tokenizer = TreebankWordTokenizer()
    token_temp = tokenizer.tokenize(text)
    for i in token_temp:
        #temp = i.decode('unicode-escape')
        #temp = re.sub(ur'[\xc2-\xf4][\x80-\xbf]+',
        #             lambda m: m.group(0).encode('latin1').decode('utf8'), temp)
        temp = unicode(i)
        temp = unicodedata.normalize('NFKD', temp).encode('ascii', 'ignore')

        # get rid of empty strings
        #temp = i
        if temp:
            token.append(temp)

    token = [clean_front_end(word) for word in token if clean_front_end(word)]

    if lower:
        token = [word.lower() for word in token]
    if stem:
        token = [stemmer.stem(word) for word in token]
    if num:
        token = [word for word in token if not is_number(word)]
    if single:
        token = [word for word in token if len(word) > 1]
    if stopword:
        token = [word for word in token if word not in STOPWORD]
    if punct:
        token = [word for word in token if word not in PUNCT]
    if link:
        token = [word for word in token if not is_link(word)]

    #exclude empty strings
    token = [word for word in token if word]

    return token


#==============================================================================
#                               text analysis
#==============================================================================

#topic
TOPIC_HEAD = open_json_file('data/topic/topic_head.json')
TOPIC_BODY = open_json_file('data/topic/topic_body.json')


#keyword
KEYWORD_HEAD = open_json_file('data/keyword/keyword_head.json')
KEYWORD_BODY = open_json_file('data/keyword/keyword_body.json')


#pos - noun
NOUN_HEAD = open_json_file('data/pos/pos_noun_head.json')
NOUN_BODY = open_json_file('data/pos/pos_noun_body.json')
#pos - adj
ADJ_HEAD = open_json_file('data/pos/pos_adj_head.json')
ADJ_BODY = open_json_file('data/pos/pos_adj_body.json')
#pos - verb
VERB_HEAD = open_json_file('data/pos/pos_verb_head.json')
VERB_BODY = open_json_file('data/pos/pos_verb_body.json')
#pos - adverb
ADVERB_HEAD = open_json_file('data/pos/pos_adverb_head.json')
ADVERB_BODY = open_json_file('data/pos/pos_adverb_body.json')
#pos - wh
WH_HEAD = open_json_file('data/pos/pos_wh_head.json')
WH_BODY = open_json_file('data/pos/pos_wh_body.json')
#pos - weird
WEIRD_HEAD = open_json_file('data/pos/pos_weird_head.json')
WEIRD_BODY = open_json_file('data/pos/pos_weird_body.json')


#ner - location
LOCATION_HEAD = open_json_file('data/ner/ner_location_head.json')
LOCATION_BODY = open_json_file('data/ner/ner_location_body.json')
#ner - organization
ORGANIZATION_HEAD = open_json_file('data/ner/ner_organization_head.json')
ORGANIZATION_BODY = open_json_file('data/ner/ner_organization_body.json')
#ner - person
PERSON_HEAD = open_json_file('data/ner/ner_person_head.json')
PERSON_BODY = open_json_file('data/ner/ner_person_body.json')
#ner - facility
FACILITY_HEAD = open_json_file('data/ner/ner_facility_head.json')
FACILITY_BODY = open_json_file('data/ner/ner_facility_body.json')
#ner - gpe
GPE_HEAD = open_json_file('data/ner/ner_gpe_head.json')
GPE_BODY = open_json_file('data/ner/ner_gpe_body.json')


def sentiment_score(text):
    try:
        text = text.decode('unicode-escape')
    except:
        return {'polarity': 0,
                'subjectivity': 0}

    sentiment = TextBlob(text).sentiment
    return {'polarity': sentiment.polarity,
            'subjectivity': sentiment.subjectivity}


def rank_semantic(text, data_dict):
    score = 0.0

    if type(data_dict) == str:
        data_dict = eval(data_dict)

    if text:
        words = tokenize(text, lower=True, punct=True, stem=True)
        for word in words:
            if word in data_dict:
                score += data_dict[word]
    return score


def get_punctuation_num(text):
    count = 0
    for i in string.punctuation:
        count += text.count(i)
    return count


def get_char_length(text):
    return len(text)


def to_string(var):
    result = ''
    try:
        result = str(var)
    except:
        pass
    return result


def get_word_length(text):
    word_num = 1
    if type(text) != str:
        text = to_string(text)
    word_num_temp = len(word_tokenize(text))
    if not word_num_temp:
        word_num = word_num_temp
    return word_num


def get_sentence_length(text):
    sentence_num = 1
    if type(text) != str:
        text = to_string(text)
    sentence_temp = len(sent_tokenize(text))
    if not sentence_temp:
        sentence_num = sentence_temp
    return sentence_num


def is_precomputed_semantic(feature):
    return feature in TEXT_FEATURE[:12]


def is_sentiment(feature):
    if feature == 'polarity' or feature == 'subjectivity':
        return True
    return False


SENT_FEATURE = {'punctuation': get_punctuation_num,
                'char_length': get_char_length,
                'word_length': get_word_length,
                'sentence_length': get_sentence_length}


def get_sent_score(text, feature):
    return SENT_FEATURE[feature](text)


def is_sentence_stats(feature):
    return feature in SENT_FEATURE.keys()


TEXT_FEATURE = ['keyword',
                'topic',
                'noun',
                'verb',
                'adj',
                'adverb',
                'weird',
                'wh',
                'person',
                'organization',
                'location',
                'gpe',
                'facility',
                'polarity',
                'subjectivity',
                'punctuation',
                'char_length',
                'word_length',
                'sentence_length']


def text_analysis(text, var_name='', head_body='body'):
    """
    @param text: string to be analyzed
    @param var_name: string for name of key of the result dict
    @param head_body: uses body text or head (title + description)

    @returns: dict with semantic feature + var_name as keys

    @todo:
    """
    semantic_data = {}

    for feature in TEXT_FEATURE:
        #assign key name
        if var_name:
            key = var_name + '_' + feature
        else:
            key = feature
            #extract features
        if is_precomputed_semantic(feature):
            data_dict = feature.upper() + '_' + head_body.upper()
            semantic_data[key] = rank_semantic(text, data_dict)
        elif is_sentiment(feature):
            semantic_data[key] = sentiment_score(text)[feature]
        elif is_sentence_stats(feature):
            semantic_data[key] = get_sent_score(text, feature)
        else:
            pass

    return semantic_data


#==============================================================================
#                               url analysis
#==============================================================================


URL_AVERAGE_LIKES = open_json_file('data/url/average_likes.json')
URL_DOMAIN_LIKES = open_json_file('data/url/domain_likes.json')
URL_ALEXA = open_json_file('data/url/alexa.json')
URL_PAGERANK = open_json_file('data/url/pagerank.json')
TLD_SCORE = open_json_file('data/url/tld_google.json')


def get_url_length(url):
    return len(url)


def get_url_level(url):
    url_path = urlparse(url).path
    levels = [i for i in url_path.split('/') if i]
    return len(levels) + 1


def get_tld_score(url):
    tld_temp = tldextract.extract(url).suffix.split('.')[-1]
    tld = '.' + tld_temp
    score = get_url_rank(tld, TLD_SCORE)
    return score


def get_url_rank(url, data_dict):
    """
    @todo: -update url database when a url in not in the data_dict
    """
    score = 0

    if type(data_dict) == str:
        data_dict = eval(data_dict)

    if url in data_dict:
        if data_dict[url]:
            score = data_dict[url]
    else:
        pass
    return score


def is_precomputed_url(feature):
    return feature in URL_FEATURE[:4]


URL_FEATURE = ['average_likes',
               'domain_likes',
               'pagerank',
               'alexa',
               'tld_score',
               'depth',
               'length']


def url_analysis(url, var_name=''):
    """
    @param url:
    @param var_name: name of key dict

    @return:

    @todo: add semantic_analysis
    """
    url_dict = {}
    url_domain = link_to_domain(url)
    for feature in URL_FEATURE:
        #set name of key
        if var_name:
            key = var_name + '_' + feature
        else:
            key = feature
            #extract data
        if is_precomputed_url(feature):
            data_dict = 'URL_' + feature.upper()
            url_dict[key] = get_url_rank(url_domain, data_dict)
        elif feature == 'depth':
            url_dict[key] = get_url_level(url)
        elif feature == 'length':
            url_dict[key] = get_url_length(url)
        elif feature == 'tld_score':
            url_dict[key] = get_tld_score(url)
        else:
            pass

    return url_dict


#==============================================================================
#                               view
#==============================================================================


#-------------------------------url--------------------------------------------

def get_url_feature(content_id=0, content_data=''):
    """
    status: required
    @todo:
    """
    url = ''

    #get data
    if content_id:
        url = Content.get_content_by_id(content_id).url
    elif content_data:
        url = content_data
    if not url:
        return {}

    #extract text from url path features
    url_path = link_to_text(url)
    text_result = text_analysis(url_path, var_name='url', head_body='head')

    #extract url features
    url_result = url_analysis(url, var_name='url')

    #combine dict data
    url_dict = dict(text_result.items() +
                    url_result.items())

    return url_dict


#----------------------------------title---------------------------------------


def get_title_feature(content_id=0, content_data=''):
    """
    status: required
    """
    title = ''

    #get data
    if content_id:
        title = Content.get_content_by_id(content_id).title
    elif content_data:
        title = content_data
    if not title:
        return {}

    #extract text feature
    title_dict = text_analysis(title, var_name='title', head_body='head')

    return title_dict

#----------------------------------date time-----------------------------------


def day_published(time_data):
    return time_data.day


def hour_published(time_data):
    return time_data.hour


def get_timestamp_feature(content_id=0, content_data=''):
    """
    status: required
    @todo:
    """
    date_dict = {}
    time_data = ''

    #get data
    if content_id:
        time_data = Content.get_content_by_id(content_id).timestamp
    elif content_data:
        time_data = content_data
    if not time_data:
        return {}

    #extract feature
    date_dict['timestamp_day'] = day_published(time_data)
    date_dict['timestamp_hour'] = hour_published(time_data)

    return date_dict


#----------------------------------description---------------------------------


def get_description_feature(content_id=0, content_data=''):
    """
    status: optional
    @todo:
    """
    desc_data = ''

    #get data
    if content_id:
        desc_data = Content.get_content_by_id(content_id).description
        #use title data for analysis
        if not desc_data:
            desc_data = Content.get_content_by_id(content_id).title
    elif content_data:
        desc_data = content_data
    if not desc_data:
        desc_data = ''

    #extact feature
    desc_dict = text_analysis(desc_data, var_name='desc', head_body='head')

    return desc_dict


#----------------------------------social--------------------------------------



def get_social_feature(content_id=0, content_data=''):
    """
    @todo: separate fb, twitter, reddit
    """
    social_dict = {}
    num_shares = 0

    #get data
    if content_id:
        data = SocialShare.get_first_social_shares_by_content_id(content_id)
        if not data:
            return {}
        num_shares = data.facebook_shares + data.retweets + data.upvotes
    elif content_data:
        num_shares = content_data
    if not num_shares:
        return {}

    #extract feature
    social_dict['shares_num'] = num_shares

    return social_dict


#----------------------------------thumbnail-----------------------------------

def get_thumbnail_feature(content_id=0, content_data=''):
    """
    status: optional
    """
    data = ''

    #get data
    if content_id:
        data = Content.get_content_by_id(content_id).image_url
    elif content_data:
        data = content_data

    #return result
    if data:
        return {'thumbnail': 1}
    else:
        return {'thumbnail': 0}


#----------------------------------icon url-----------------------------------

def get_icon_feature(content_id=0, content_data=''):
    """
    status: optional
    """
    data = ''

    #get data
    if content_id:
        data = Content.get_content_by_id(content_id).icon_url
    elif content_data:
        data = content_data

    #return result
    if data:
        return {'icon': 1}
    else:
        return {'icon': 0}


#----------------------------------content type--------------------------------

def get_content_type_feature(content_id=0, content_data=''):
    """
    status: optional
    """
    data = 0

    #get data
    if content_id:
        data_temp = Content.get_content_by_id(content_id).type_id
        if data_temp:
            if data_temp.isdigit():
                data = int(data_temp)
    elif content_data:
        data = content_data

    if not data:
        content_type = 0
    else:
        content_type = data.id

    return {'content_type': content_type}


#==================================aggregate features==========================


def view_data(content_id=0, content_data={}):
    """
    @param content_data: dict with the following keys:
        1. url
        2. title
        3. timestamp
        4. description
        5. social - fb likes + retweets + upvotes
        6. thumbnail - article thumbnail
        7. icon_url - website icon
        8. type_id - content type; article, video, pic
    """
    url_data = ''
    title_data = ''
    date_data = ''
    description_data = ''
    social_data = ''
    thumbnail_data = ''
    icon_data = ''
    content_type_data = 0

    if content_data:
        url_data = content_data['url']
        title_data = content_data['title']
        date_data = content_data['timestamp']
        description_data = content_data['description']
        if not description_data:
            description_data = title_data
        if 'social' in content_data:
            social_data = content_data['social']
        thumbnail_data = content_data['thumbnail']
        icon_data = content_data['icon_url']
        content_type_data = content_data['type_id']

    url = get_url_feature(content_id=content_id,
                          content_data=url_data)

    title = get_title_feature(content_id=content_id,
                              content_data=title_data)

    date = get_timestamp_feature(content_id=content_id,
                                 content_data=date_data)

    description = get_description_feature(content_id=content_id,
                                          content_data=description_data)

    if content_id or social_data:
        social = get_social_feature(content_id=content_id,
                                    content_data=social_data)

    thumbnail = get_thumbnail_feature(content_id=content_id,
                                      content_data=thumbnail_data)

    icon = get_icon_feature(content_id=content_id,
                            content_data=icon_data)

    content_type = get_content_type_feature(content_id=content_id,
                                            content_data=content_type_data)

    result = dict(url.items() +
                  title.items() +
                  date.items() +
                  description.items() +
                  thumbnail.items() +
                  icon.items() +
                  content_type.items())

    if content_id or social_data:
        result = dict(result.items() + social.items())

    return result


#==============================================================================
#                               understand
#==============================================================================

#----------------------------------body----------------------------------------

def get_text(content_id):
    raw_html = Content.get_raw_html_by_id(content_id)
    try:
        text = Extractor(extractor='ArticleExtractor', html=raw_html).getText()
    except:
        return ''
    return text


def get_body_feature(content_id=0, content_data='', html_data=''):
    """
    status: optional
    """
    text_data = ''

    #get data
    if content_id:
        text_data = get_text(content_id)
    elif content_data:
        text_data = content_data
    elif html_data:
        text_data = html_to_text(html_data)
    if not text_data:
        text_data = ''

    #extract features
    text_dict = text_analysis(text_data, var_name='body')

    return text_dict


#----------------------------------html----------------------------------------

HTML_HEAD = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
HTML_A = ['a']
HTML_P = ['p']
HTML_EMBED = ['img', 'svg', 'iframe', 'embed', 'video', 'canvas', 'area', 'map']
HTML_STYLE = ['em', 'strong', 'cite', 'code', 'center', 'i']
HTML_LAYOUT = ['br', 'ol', 'ul', 'li', 'div', 'span', 'table']
HTML_META = ['meta', 'link', 'cite']
HTML_INPUT = ['form', 'button', 'textarea', 'input', 'select', 'fieldset']
HTML_SCRIPT = ['script', 'noscript']


def get_html_num(soup):
    return len(soup.find_all(True))


def get_html_tags(soup, tags):
    count = 0
    for tag in tags:
        count += len(soup.find_all(tag))

    return count


def get_html_feature(content_id=0, content_data='', html_data=''):
    """
    status: required
    @param content_data: BeautifulSoup object
    @param html_data: html string
    """
    html_dict = {}
    soup = ''

    #get data
    if content_id:
        html_data = Content.get_raw_html_by_id(content_id)
        try:
            soup = BeautifulSoup(html_data)
        except:
            pass
    elif content_data:
        soup = content_data
    elif html_data:
        try:
            soup = BeautifulSoup(html_data)
        except:
            pass
    if not soup:
        return {}

    #extract features
    html_dict['html_num'] = get_html_num(soup)
    html_dict['html_h'] = get_html_tags(soup, HTML_HEAD)
    html_dict['html_a'] = get_html_tags(soup, HTML_A)
    html_dict['html_p'] = get_html_tags(soup, HTML_P)
    html_dict['html_embed'] = get_html_tags(soup, HTML_EMBED)
    html_dict['html_style'] = get_html_tags(soup, HTML_STYLE)
    html_dict['html_layout'] = get_html_tags(soup, HTML_LAYOUT)
    html_dict['html_meta'] = get_html_tags(soup, HTML_META)
    html_dict['html_input'] = get_html_tags(soup, HTML_INPUT)
    html_dict['html_script'] = get_html_tags(soup, HTML_SCRIPT)

    return html_dict

#----------------------------------heading tag---------------------------------


def get_heading_word(soup_data):
    """
    get text in heading tags
    """
    h_tags = []
    for h in HTML_HEAD:
        h_tags += soup_data.find_all(h)
    heading_temp = []
    for tag in h_tags:
        if tag.string:
            heading_temp += tag.string.split()
    heading_words = ' '.join(heading_temp)
    return heading_words


def get_heading_feature(content_id=0, content_data='', html_data=''):
    """
    status: optional
    """
    soup_data = ''

    #get data
    if content_id:
        html = Content.get_raw_html_by_id(content_id)
        try:
            soup_data = BeautifulSoup(html)
        except:
            pass
    elif content_data:
        soup_data = content_data
    elif html_data:
        try:
            soup_data = BeautifulSoup(html_data)
        except:
            pass
    if not soup_data:
        soup_data = BeautifulSoup('')

    #extract h tags and features
    heading_data = get_heading_word(soup_data)
    heading_dict = text_analysis(heading_data, var_name='heading')

    return heading_dict


#----------------------------------anchor tag----------------------------------


def sum_list_dict(list_dict, var_name):
    """
    sum value in a list of dicts
    @param list_dict: [{val1},{val2}]
    @return: {val1 + val2}
    """
    result_dict = {}

    #name of keys
    keys = [var_name + '_' + feat for feat in URL_FEATURE]
    for elt in list_dict:
        for key in keys:
            if key in result_dict and key in elt:
                result_dict[key] += elt[key]
            elif key in elt:
                result_dict[key] = elt[key]
            else:
                result_dict[key] = 0

    return result_dict


def get_anchor(soup_data):
    a_tags = []
    #find a tags in p tags
    try:
        p_tags = soup_data.find_all('p')
        for p in p_tags:
            if p:
                temp_tag = p.find_all('a')
                if temp_tag:
                    a_tags += temp_tag
    except:
        print 'wong wong wong algorithm.py in get_anchor'
        pass
    return a_tags


def get_anchor_feature(content_id=0, content_data='', html_data=''):
    """
    a tags in p tags
    @status: optional
    @param content_data: BeautifulSoup object
    @param html_data: html string
    @todo:
    """
    soup_data = ''
    anchor_text = []
    anchor_link = []

    #get data
    if content_id:
        raw_html = Content.get_raw_html_by_id(content_id)
        try:
            soup_data = BeautifulSoup(raw_html)
        except:
            pass
    elif content_data:
        soup_data = content_data
    elif html_data:
        try:
            soup_data = BeautifulSoup(html_data)
        except:
            pass
    if not soup_data:
        soup_data = BeautifulSoup('')

    #get a tags links and text
    anchor_data = get_anchor(soup_data)
    for a in anchor_data:
        if a.string:
            anchor_text += a.string.split()
            if a.has_attr('href'):
                anchor_link.append(a['href'])

    #run thru text analysis even with empty soup cause of the loops(fixed bug)
    if not anchor_link:
        anchor_link = ['']

    #extract text features
    anchor_text = ' '.join(anchor_text)
    text_result = text_analysis(anchor_text, var_name='anchor')

    #extract link features
    url_list = []
    for link in anchor_link:
        url_list.append(url_analysis(link, var_name='anchor'))
    url_result = sum_list_dict(url_list, 'anchor')

    anchor_dict = dict(text_result.items() +
                       url_result.items())

    return anchor_dict

#===============================aggregate features=============================


def access_data(content_id=0, content_data={}):
    """
    @param content_data: html string
    """
    soup = ''
    text_data = ''

    if content_data:
        html_data = content_data['raw_html']
        text_data = html_to_text(html_data)
        try:
            soup = BeautifulSoup(html_data)
        except:
            return {}

    text = get_body_feature(content_id=content_id,
                            content_data=text_data)
    html_tag = get_html_feature(content_id=content_id,
                                content_data=soup)
    heading = get_heading_feature(content_id=content_id,
                                  content_data=soup)
    anchor = get_anchor_feature(content_id=content_id,
                                content_data=soup)

    return dict(text.items() +
                html_tag.items() +
                anchor.items() +
                heading.items())


#==============================================================================
#                               agree
#==============================================================================


#==============================================================================
#                               ratio
#==============================================================================


"""
char/word
word/sent
punctuation/word

word/html
h/html
a/html
p/html

EMBED
STYLE
LAYOUT
META
INPUT
SCRIPT
"""

RATIO_FEATURE = {'ratio_char_word': ['body_char_length', 'body_word_length'],
                 'ratio_word_sent': ['body_word_length', 'body_sentence_length'],
                 'ratio_punctuation_word': ['body_punctuation', 'body_word_length'],
                 'ratio_title_word': ['title_word_length', 'body_word_length'],
                 'ratio_desc_word': ['desc_word_length', 'body_word_length'],
                 'ratio_a_word': ['anchor_word_length', 'body_word_length'],
                 'ratio_word_html': ['body_word_length', 'html_num'],
                 'ratio_h_html': ['html_h', 'html_num'],
                 'ratio_a_html': ['html_a', 'html_num'],
                 'ratio_p_html': ['html_p', 'html_num'],
                 'ratio_embed_html': ['html_embed', 'html_num'],
                 'ratio_style_html': ['html_style', 'html_num'],
                 'ratio_layout_html': ['html_layout', 'html_num'],
                 'ratio_meta_html': ['html_meta', 'html_num'],
                 'ratio_input_html': ['html_input', 'html_num'],
                 'ratio_script_html': ['html_script', 'html_num']}


def get_ratio(num, denom):
    if not denom:
        return 0.0
    return num / float(denom)


def get_ratio_feature(data_dict):
    """
    @param data_dict: {key1:[feat1,feat2],key2:{feat1,feat2}}
    @returns: ratios feature
    """
    ratio_dict = {}

    for feature in RATIO_FEATURE:
        num = RATIO_FEATURE[feature][0]
        denom = RATIO_FEATURE[feature][1]
        """
        @bug:
        KeyError: 'html_h'
        ERROR: An unexpected error occurred while tokenizing input
        The following traceback may be corrupted or invalid
        The error message is: ('EOF in multi-line string', (1, 4))
        """
        try:
            ratio_dict[feature] = get_ratio(data_dict[num], data_dict[denom])
        except:
            print 'errorrrrrr in get_ratio_feature algorithnm'
            return {}

    return ratio_dict


#-------------------------------target-----------------------------------------


def get_target(content_id):
    """
    get the last social shares from database
    """
    data = SocialShare.get_last_social_shares_by_content_id(content_id)
    if not data:
        return
    return data.facebook_shares + data.retweets + data.upvotes


#==============================================================================
#                               main
#==============================================================================





