import HTMLParser
import nltk

STRING_LITERAL = ['\n', '\\']
htmlParser = HTMLParser.HTMLParser()

def join_root_with_domain(domain_url, join_url):
    root_idx = domain_url.find('/', 7)
    join_url = domain_url[:root_idx] + join_url
    return join_url

def get_og_property(soup, og_prop):
    node = soup.find('meta', {'property': 'og:' + og_prop})
    return get_content_from_node(node)

def get_twitter_property(soup, tw_prop):
    node = soup.find('meta', {'name': 'twitter:' + tw_prop})
    return get_content_from_node(node)

def get_meta_property(soup, meta_prop):
    node = soup.find('meta', {'name': meta_prop})
    return get_content_from_node(node)

def get_content_from_node(node):
    if node:
        content = node.get('content')
        if content:
            return clean_html(content)
    return None

def remove_non_ascii(s): return "".join(i for i in s if ord(i)<128)

def clean_html(html_string):
    """
    strip html tags and escape html char

    @todo: deal with string literal
           convert unicode to string - http://stackoverflow.com/questions/1207457/convert-unicode-to-string-in-python-containing-extra-symbols
    """
    #get rid of html tags using
    text = nltk.clean_html(html_string)
    #replace trash char
    for char in STRING_LITERAL:
        text.replace(char, '')

    text = remove_non_ascii(text)
    text = htmlParser.unescape(text)
    return text