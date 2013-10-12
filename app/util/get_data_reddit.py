import feedparser
import requests
import time
from app import db
from app.models.Content import Content
from get_data import url_content


REDDIT_RSS = ['http://www.reddit.com/r/news/new/.rss?limit=100',
              'http://www.reddit.com/r/worldnews/new/.rss?limit=100']


'''
REDDIT_RSS = ['http://www.reddit.com/r/news/.rss?limit=100',
              'http://www.reddit.com/r/news/new/.rss?limit=100',
              'http://www.reddit.com/r/worldnews/.rss?limit=100',
              'http://www.reddit.com/r/worldnews/new/.rss?limit=100']

REDDIT_RSS += ['http://www.reddit.com/r/technology/.rss?limit=100',
              'http://www.reddit.com/r/business/.rss?limit=100']

REDDIT_RSS += ['http://www.reddit.com/r/videos/.rss?limit=100',
               'http://www.reddit.com/.rss?limit=100']
'''

def rss_data(url):

    data = []
    
    #try parse rss feed
    try:
        content = feedparser.parse(url)
    except:
        print 'Problem parsing url: ' + url
        return 

    #extract data 
    for i in content.entries:
        dictData = {}
        dictData['title'] = i.title
        dictData['timestamp'] = i.published_parsed
        
        #reddit comment section url
        dictData['raw_url'] = i.link
        url_reddit_comment = i.link
            
        #check if url ends with a '/'
        if url_reddit_comment[-1] != '/':
            url_reddit_comment += '/'
    
        #open reddits url with json format
        try:
            page = requests.get(url_reddit_comment+'.json').json()
        except:
            print 'this URL:' + url_reddit_comment + ' cannot be oppened'
            continue

        #get data from reddit comment url
        url_reddit_content = page[0]['data']['children'][0]['data']['url'] 
        dictData['upvotes'] = page[0]['data']['children'][0]['data']['ups']
        
        #get the content if url is valid                                                     
        urlContentData = url_content(url_reddit_content)
        if urlContentData:
            dictData = dict(dictData.items() + urlContentData.items())
        else:
            print 'No content for url:' + url_reddit_content
            continue
        '''
        #get social count from both reddit comment url and reddit url content
        social1 = social_count(url_reddit_comment,reddit=False)       
        social2 = social_count(url_reddit_content,reddit=False)
        
        #adding dict social1 and social2
        social = dict( (n, social1.get(n, 0)+social2.get(n, 0)) for n in set(social1)|set(social2) )
        dictData = dict(dictData.items() + social.items())
        '''

        #store dict in list 
        data.append(dictData)
        time.sleep(1)
    
    return data


def get_data_reddit():

    for url in REDDIT_RSS:
        data = rss_data(url)
        for content in data:
            print 'Storing data from ' + url
            print 'TITLE:' + content['title'] + ' URL: ' + content['url']
            print '------------------------------------------------------'
            time.sleep(0.5)
            Content.getOrCreateContent(db.session,**content)
        db.session.commit()
        


