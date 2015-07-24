#!/usr/bin/env python

from datetime import datetime, timedelta
import json
from pprint import pprint
import time
import urllib
import urllib2

def load_configuration():
    with open('donut.json', 'r') as data:
        config = json.load(data)
    return config


def send_notification(message):
    proxies = {}
    
    if config['proxy']['enabled'] == "1":
        proxy_auth_url = "http://%s:%s@%s:%s" % (config['proxy']['username'],
                                                 config['proxy']['password'],
                                                 config['proxy']['url'],
                                                 config['proxy']['port'])
        pprint(proxy_auth_url)
        proxies = {'http': proxy_auth_url,
                   'https': proxy_auth_url}

    proxy_handler = urllib2.ProxyHandler(proxies)
    opener = urllib2.build_opener(proxy_handler)
    payload = urllib.urlencode({'token': config['pushover']['api_token'],
                                'user': config['pushover']['user_key'],
                                'message': message, })
        
    request = urllib2.Request(config['pushover']['url'], data=payload,
                              headers={'Content-type': 'application/x-www-form-urlencoded'})
        
    result = opener.open(request)
    pprint(result.geturl())
    pprint(str(result.info()))
    pprint(result.getcode())


def get_jenkins_job_status(job):
    url = "%s/%s/%s" % (config['jenkins']['url'], job, config['jenkins']['suffix'])

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


def construct_message(data):
    completeAt = datetime.fromtimestamp(data['timestamp'] / 1000)
    result = data['result']
    if result == None and data['building'] == True:
        result = "In progress"
    message = "%s:\n%s at %s" % (data['fullDisplayName'], result.capitalize(), completeAt)
    return message


if __name__ == "__main__":
    config = load_configuration()

    results = []

    for job in config['jenkins']['jobs']:
        data = get_jenkins_job_status(job)
        if data:
            results.append(data)
            message = construct_message(data)
            send_notification(message)
            time.sleep(5)

    pprint(results)
