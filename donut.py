#!/usr/bin/env python

import json
from pprint import pprint
import urllib
import urllib2

if __name__ == "__main__":
	with open('donut.json', 'r') as config:
		data = json.load(config)
		pprint(data)
			
	if data['proxy']['enabled'] == "1":
		proxy_auth_url = "http://%s:%s@%s:%s" % (data['proxy']['username'],
												 data['proxy']['password'],
												 data['proxy']['url'],
												 data['proxy']['port'])
		pprint(proxy_auth_url)
		proxy_handler = urllib2.ProxyHandler({'http': proxy_auth_url,
		                                      'https': proxy_auth_url})
	else:
		proxy_handler = urllib2.ProxyHandler({})
	
	opener = urllib2.build_opener(proxy_handler)
	payload = urllib.urlencode({'token': data['pushover']['api_token'],
	                            'user': data['pushover']['user_key'],
	                            'message': 'Hello World', })
	
	request = urllib2.Request(data['pushover']['url'], data=payload,
	                          headers={'Content-type': 'application/x-www-form-urlencoded'})
	                          
	result = opener.open(request)
	pprint(result.geturl())
	pprint(str(result.info()))
	pprint(result.getcode())
