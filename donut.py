#!/usr/bin/env python

from datetime import datetime, timedelta
import json
from pprint import pprint
import time
import urllib
import urllib2

def send_notification(message):
    with open('donut.json', 'r') as config:
        data = json.load(config)
        #pprint(data)

    proxies = {}
    
    if data['proxy']['enabled'] == "1":
        proxy_auth_url = "http://%s:%s@%s:%s" % (data['proxy']['username'],
                                                 data['proxy']['password'],
                                                 data['proxy']['url'],
                                                 data['proxy']['port'])
        pprint(proxy_auth_url)
        proxies = {'http': proxy_auth_url,
                   'https': proxy_auth_url}

    proxy_handler = urllib2.ProxyHandler(proxies)
    opener = urllib2.build_opener(proxy_handler)
    payload = urllib.urlencode({'token': data['pushover']['api_token'],
                                'user': data['pushover']['user_key'],
                                'message': message, })
        
    request = urllib2.Request(data['pushover']['url'], data=payload,
                              headers={'Content-type': 'application/x-www-form-urlencoded'})
        
    result = opener.open(request)
    pprint(result.geturl())
    pprint(str(result.info()))
    pprint(result.getcode())


def get_jenkins_job_status(job):
    url = "%s/%s/%s" % (JENKINS_URL, job, URL_SUFFIX)

    proxies = {}
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)

    data = None
    try:
        request = urllib2.Request(url)
        response = opener.open(request)
        data = json.loads(response.read())
        pprint(data)
    except urllib2.HTTPError as e:
        pprint(str(e))
        pprint(url)
    return data


if __name__ == "__main__":
    #send_notification('This is a test message')
    proxies = {}
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)

    JENKINS_URL = 'http://10.216.10.221:8888/jenkins/view/C755A/job'
    URL_SUFFIX = 'lastBuild/api/json'

    # Add more jobs later
    JOBS = ['C755A-Build-DatabaseRpmLinux']

    for job in JOBS:
        data = get_jenkins_job_status(job)
        if data:
            duration = timedelta(seconds = data['duration'] / 1000)
            completeAt = datetime.fromtimestamp(data['timestamp'] / 1000)
            message = "%s:\n%s at %s" % (data['fullDisplayName'], data['result'], completeAt)
            send_notification(message)
