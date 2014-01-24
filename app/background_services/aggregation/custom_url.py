import requests
from bs4 import BeautifulSoup

def is_fark(url):
    return url.startswith('http://rss.feedsportal.com/c/35344/f/661517/')

def is_newsvine(url):
    return 'newsvine.com' in url

def is_vitals(url):
    return 'vitals.nbcnews.com' in url

def is_imgur_image(url):
    return 'i.imgur.com' in url

def is_reddit(url):
    return 'reddit.com' in url

def get_raw_url_for_fark(url):
    soup = BeautifulSoup(requests.get(url).text)
    return soup.find('a', {'class': 'outbound_link'})['href']

def get_raw_url_for_newsvine(url):
    soup = BeautifulSoup(requests.get(url).text)
    return soup.find('span', {'class': 'c-seed-source'}).a['href']

def get_raw_url_for_vitals(url):
    soup = BeautifulSoup(requests.get(url).text)
    return soup.find('div', {'class': 'c-seed-link'}).a['href']

def get_imgur_image_raw_url(url):
    return url[:url.rfind('.')]

def get_reddit_raw_url(url):
    if url[-1] != '/':
        url += '/'
    page = requests.get(url + '.json').json()
    return page[0]['data']['children'][0]['data']['url']