import requests
from bs4 import BeautifulSoup as bs



def get_metadata(url):
    data = {}

    try:
        pageReq = requests.get(url)
    except:
        #print error message
        print 'cannot open page in get metadata'
        return data

    soup = bs(pageReq.text)
    
    #find title
    title = ''
    title_data1 = soup.find('meta',{'property':'og:title'})
    title_data2 = soup.find('meta',{'name':'title'})
    title_data3 = soup.find('meta',{'name':'twitter:title'})
    if title_data1:
        title = title_data1.get('content')
    elif title_data2:
        title = title_data2.get('content')
    elif title_data3:
        title = title_data3.get('content')
    if title: data['title']=title

    #find description
    desc = ''
    desc_data1 = soup.find('meta',{'property':'og:description'})
    desc_data2 = soup.find('meta',{'name':'description'})
    desc_data3 = soup.find('meta',{'name':'twitter:description'})
    if desc_data1:
        desc = desc_data1.get('content')
    elif desc_data2:
        desc = desc_data2.get('content')
    elif desc_data3:
        desc = desc_data3.get('content')
    if desc: data['description']=desc

    #find type
    type_id = ''
    type_data1 = soup.find('meta',{'property':'og:type'})
    type_data2 = ''
    type_data2_temp = pageReq.headers
    if 'content-type' in type_data2_temp: type_data2=type_data2_temp['content-type']
    if type_data1:
        type_id = type_data1.get('content')
    elif type_data2:
        type_id = type_data2
        if 'text' in type_data2: type_id='text'
        if 'image' in type_data2: type_id='image'
    if type_id: data['type_id']=type_id
    
    #find keywords
    keywords = ''
    keyword_data1 = soup.find('meta',{'name':'keywords'})
    keyword_data2 = soup.find('meta',{'name':'news_keywords'})
    if keyword_data1:
        keywords = keyword_data1.get('content')
    if keyword_data2:
        keywords_temp = keyword_data2.get('content')
        keywords += ', ' + keyword_temp
    if keywords: data['meta_tags']=keywords

    #find image_url
    image_url = ''
    image_data1 = soup.find('meta',{'property':'og:image'})
    image_data2 = soup.find('meta',{'name':'twitter:image'})
    if image_data1:
        image_url = image_data1.get('content')
    elif image_data2:
        image_url = image_data2.get('content')
    if image_url: data['image_url']=image_url

    return data
    





    
    
        
    
    
