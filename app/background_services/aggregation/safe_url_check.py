__author__ = 'sysofwan'
from util import get_root_url
import requests

domain_cache = {}

SAFE_API_KEY = 'ABQIAAAAdS7aOcCGjyFzKoFFY92IYRTHO0quRfx4lETdac9rtF1fh_5mEw'
SAFE_API_URL = 'https://sb-ssl.google.com/safebrowsing/api/lookup?client=api&apikey=%s&appver=1.0&pver=3.0&url=%s'

def is_safe_url(url):
    root_url = get_root_url(url)
    url = SAFE_API_URL %(SAFE_API_KEY, root_url)
    req = requests.get(url)
    return req.text == ''
