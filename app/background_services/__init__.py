import requests

reqSession = requests.Session()
reqSession.headers.update({'User-Agent': 'Zapfeedsbot (+http://zapfeeds.com/contact)'})