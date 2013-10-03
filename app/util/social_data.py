import requests

def social_count(url,reddit=True):	
	data = {'facebook_shares':0,'retweets':0}

	#get facebooks share

	try:
		fb_temp = requests.get('https://graph.facebook.com/?ids='+url).json()
		data['facebook_shares'] = fb_temp[url]['shares']
	except KeyError:
		fb_temp = requests.get('https://graph.facebook.com/'+url).json()
		if 'shares' in fb_temp:
			data['facebook_shares'] = fb_temp['shares']
	except:
		pass
		
	#get twitters retweet
	twit_temp = requests.get('http://urls.api.twitter.com/1/urls/count.json?url='+url).json()
	if 'count' in twit_temp:
		data['retweets'] = twit_temp['count']
	
	#if reddits upvote data is not required, return data
	if reddit == False:
		return data
	
	data['upvotes'] = 0

	#get reddits upvote
	try:
		redditRedirectReq = requests.get('http://www.reddit.com/'+url)
		reddit_url = redditRedirectReq.url
		if reddit_url[-1] != '/':
			reddit_url += '/'
		reddit_url += '.json'
		reddit_temp = requests.get(reddit_url).json()
		data['upvotes'] = reddit_temp[0]['data']['children'][0]['data']['ups']
	except:
	      	pass

	return data

