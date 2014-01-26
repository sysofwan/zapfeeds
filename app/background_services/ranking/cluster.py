import nltk
import math
import numpy
import operator
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from scipy.cluster.hierarchy import linkage
from algorithm import query_database


lemmatizer = WordNetLemmatizer()


#==============================================================================
#================================get data======================================
#==============================================================================


def get_data():
    """
    todo:
    get text from db? html?
    """
    query = '''
            select
            id, title, description
            from
            contents
            '''
    data = query_database(query)
    data = [list(row) for row in data]
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
        words_list = [lemmatizer.lemmatize(word) for word in words_list if
                      len(word) > 1 and
                      word.isalpha() and
                      word not in stopwords.words('english')]
        corpus.append(words_list)
        titles.append(title)
        print 'Title: ', title

    return titles, corpus


#==============================================================================
#================================tf-idf score==================================
#==============================================================================

def freq(word, document):
    return document.count(word)


def wordCount(document):
    return len(document)


def numDocsContaining(word, documentList):
    count = 0
    for document in documentList:
        if freq(word, document) > 0:
            count += 1
    return count


def tf(word, document):
    return (freq(word, document) / float(wordCount(document)))


def idf(word, documentList):
    return math.log(len(documentList) / numDocsContaining(word, documentList))


def tfidf(word, document, documentList):
    return (tf(word, document) * idf(word, documentList))


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

def extract_clusters(Z, threshold, n):
    clusters = {}
    ct = n
    for row in Z:
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


def cluster(data_list, threshold=0.9, n_keywords=5):
    """
    data_list: <id>, <title>, <description>
    returns: clusters with keyword:[<id1>,<id2>,...,<idn>]
    """

    clusters = {}
    titles, corpus = populate_data([data[1:] for data in data_list])
    key_word_list = set()

    for doc in corpus:
        for top_words in top_keywords(n_keywords, doc, corpus):
            key_word_list.add(top_words)

    feature_vec = feature_vector(corpus, key_word_list)
    matrix = create_matrix(len(corpus), feature_vec)
    Z = linkage(matrix)
    clusters_dict = extract_clusters(Z, threshold, len(corpus))
    keyword_id_dict = keyword_cluster(clusters_dict, key_word_list, feature_vec)

    for key in keyword_id_dict:
        print '==============================='
        print 'Keyword: ', key
        clusters_temp = []
        for link_id in keyword_id_dict[key]:
            clusters_temp.append(data_list[link_id][0])
            print 'ID: ', data_list[link_id][0], ' Title: ', data_list[link_id][1]
        clusters[key] = clusters_temp

    return clusters

















