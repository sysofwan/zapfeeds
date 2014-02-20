import nltk
import math
import numpy
import time
import operator
from nltk.corpus import stopwords
#from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from scipy.cluster.hierarchy import linkage
from app.models.Content import Content
from datetime import timedelta

#lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()


#==============================================================================
#================================get data======================================
#==============================================================================


def id_from_database():
    ids = [elt.id for elt in Content.query.all()]
    return ids


def get_data(news_number=1000):
    """
    todo:
    get text from db? html?
    """
    data = []
    counter = 0
    ids = id_from_database()
    for news_id in ids:
        if counter >= news_number:
            break
        content = Content.get_content_by_id(news_id)
        title = content.title
        description = content.description
        if not description:
            description = title
        data.append([news_id, title, description])
        counter += 1

    return data


#==============================================================================
#================================populate data=================================
#==============================================================================


def populate_data(data_list):
    """
    data_list: <title>, <description>
    """

    titles = []
    corpus = []

    for row in data_list:
        title = row[0]
        if row[1]:
            desc = row[1]
        else:
            desc = title

        words_list = nltk.wordpunct_tokenize((title + desc).lower())
        words_list = [stemmer.stem(word) for word in words_list if
                      len(word) > 1 and
                      word.isalpha() and
                      word not in stopwords.words('english')]
        corpus.append(words_list)
        titles.append(title)

    return titles, corpus


#==============================================================================
#================================tf-idf score==================================
#==============================================================================

def freq(word, document):
    return document.count(word)


def word_count(document):
    return len(document)


def num_docs_containing(word, document_list):
    count = 0
    for document in document_list:
        if freq(word, document) > 0:
            count += 1
    return count


def tf(word, document):
    return freq(word, document) / float(word_count(document))


def idf(word, document_list):
    return math.log(len(document_list) / num_docs_containing(word, document_list))


def tfidf(word, document, document_list):
    return tf(word, document) * idf(word, document_list)


#==============================================================================
#================================tf-idf score==================================
#==============================================================================


def top_keywords(n_keywords, doc, corpus):
    d = {}
    for word in set(doc):
        if word.isalpha():
            d[word] = tfidf(word, doc, corpus)
    sorted_d = sorted(d.iteritems(), key=operator.itemgetter(1), reverse=True)

    return [w[0] for w in sorted_d[:n_keywords]]


#==============================================================================
#================================feature vec===================================
#==============================================================================

def feature_vector(corpus, key_word_list):
    feature_vec = []
    for document in corpus:
        vec = []
        for word in key_word_list:
            if word in document:
                vec.append(tfidf(word, document, corpus))
            else:
                vec.append(0)
        feature_vec.append(vec)
    return feature_vec


#==============================================================================
#================================matrix========================================
#==============================================================================

def create_matrix(n, feature_vec):
    mat = numpy.empty((n, n))

    for i in xrange(0, n):
        for j in xrange(0, n):
            feat_vec1 = feature_vec[i]
            feat_vec2 = feature_vec[j]
            mat[i][j] = nltk.cluster.util.cosine_distance(feat_vec1, feat_vec2)
    return mat


#==============================================================================
#================================extract cluster===============================
#==============================================================================

def extract_clusters(z, threshold, n):
    clusters = {}
    ct = n
    for row in z:
        if row[2] < threshold:
            n1 = int(row[0])
            n2 = int(row[1])

            if n1 >= n:
                l1 = clusters[n1]
                del (clusters[n1])
            else:
                l1 = [n1]

            if n2 >= n:
                l2 = clusters[n2]
                del (clusters[n2])
            else:
                l2 = [n2]
            l1.extend(l2)
            clusters[ct] = l1
            ct += 1
        else:
            return clusters


#==============================================================================
#================================keyword=======================================
#==============================================================================


def word_from_list(place_holder, key_word_list):
    weight_list = []
    for i in range(len(key_word_list)):
        weight_temp = 0
        for doc in place_holder:
            weight_temp += doc[i][1]
        weight_list.append(weight_temp)
    max_weight = weight_list.index(max(weight_list))
    return key_word_list[max_weight]


#==============================================================================
#================================keyword cluster===============================
#==============================================================================


def keyword_cluster(cluster_dict, key_word_list, feature_vec):
    key_word_list = list(key_word_list)
    keyword_id_dict = {}

    for key in cluster_dict:
        place_holder = []
        clusters = cluster_dict[key]
        for doc in clusters:
            temp = []
            for i in range(len(key_word_list)):
                temp.append([key_word_list[i], feature_vec[doc][i]])
            place_holder.append(temp)
        word = word_from_list(place_holder, key_word_list)
        keyword_id_dict[word] = clusters

    return keyword_id_dict


#==============================================================================
#================================main function=================================
#==============================================================================


def cluster_news(data_list, threshold=0.9, train=False):
    """
    data_list: <id>, <title>, <description>
    returns: clusters [[<id1>,<id2>,...,<idn>]...]
    """
    start_time = time.time()
    clusters = {}
    n_keywords = choose_number_of_keywords(len(data_list))
    titles, corpus = populate_data([data[1:] for data in data_list])
    key_word_list = set()

    for doc in corpus:
        for top_words in top_keywords(n_keywords, doc, corpus):
            key_word_list.add(top_words)

    feature_vec = feature_vector(corpus, key_word_list)
    matrix = create_matrix(len(corpus), feature_vec)
    z = linkage(matrix)
    clusters_dict = extract_clusters(z, threshold, len(corpus))
    keyword_id_dict = keyword_cluster(clusters_dict, key_word_list, feature_vec)

    end_time = time.time()

    for key in keyword_id_dict:
        print '==============================='
        print 'Keyword: ', key
        clusters_temp = []
        for link_id in keyword_id_dict[key]:
            clusters_temp.append(data_list[link_id][0])
            print 'ID: ', data_list[link_id][0], ' Title: ', data_list[link_id][1]
        clusters[key] = clusters_temp

    if train:
        print '\n=========== stats ===========\n'
        print 'data count: ', len(data_list)
        print 'threshold: ', threshold
        print 'number of keywords: ', n_keywords
        print 'total running time: ', str(timedelta(seconds=end_time - start_time)), '\n'

    return [clusters[keyword] for keyword in clusters]


def choose_number_of_keywords(num_of_data):
    if num_of_data <= 500:
        return 3
    else:
        return 2


def update_parent_cluster(clusters, contents, session):
    """
    """
    id_cluster = format_cluster(clusters)
    content_ids = [row[0] for row in contents]
    for content_id in content_ids:
        content = Content.get_content_by_id(content_id)
        if not content.parent_cluster:
            content.parent_cluster = id_cluster[content_id] if content_id in id_cluster else 0
            session.add(content)
        else:
            #update contents previously clustered
            if content_id in id_cluster:
                clustered_contents = Content.get_content_by_parent_cluster(content.parent_cluster)
                for clustered_content in clustered_contents:
                    clustered_content.parent_cluster = id_cluster[content_id]
                    session.add(clustered_content)
    session.commit()


def format_cluster(clusters):
    """
    @todo: improve selection of parent cluster (currently using smalled id)
            - 2 factors: freshness and rank of the content
    """
    id_dict = {}
    for cluster in clusters:
        parent_cluster = min(cluster)
        for elt in cluster:
            id_dict[elt] = parent_cluster
    return id_dict








