#!/usr/bin/env python

from datetime import datetime, timedelta
import json
from pprint import pprint
import time
import urllib
import urllib2

#
# Load data from a JSON file
#
def load_json_file(filename):
    try:
        with open(filename, 'r') as infile:
            data = json.load(infile)
    except IOError as e:
        pprint(str(e))
        data = None
    return data


#
# Save data to a JSON file
#
def save_json_file(filename, data):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

   
#
# Send notification to Pushover.net
#
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
    
    try:
        result = opener.open(request)
        pprint(result.geturl())
        pprint(str(result.info()))
        pprint(result.getcode())
    except urllib2.URLError as e:
        pprint(str(e))


#
# Get Jenkins' job status from Jenkins server
#
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
        #pprint(data)
    except urllib2.HTTPError as e:
        pprint(str(e))
        pprint(url)
    return data


#
# Create a message to be sent as a notification
#
def construct_message(data):
    completeAt = datetime.fromtimestamp(data['timestamp'] / 1000)
    result = data['result']
    if result == None and data['building'] == True:
        result = "In progress"
    message = "%s:\n%s at %s" % (data['fullDisplayName'], result.capitalize(), completeAt)
    return message


if __name__ == "__main__":
    config = load_json_file('donut.json')

    for job in config['jenkins']['jobs']:
        data = get_jenkins_job_status(job)
        if data:
            prevData = load_json_file("%s.json" % (job))
            if prevData == None:
                # No previous data so send this message
                message = construct_message(data)
                send_notification(message)
            else:
                if data['fullDisplayName'] != prevData['fullDisplayName']:
                    message = construct_message(data)
                    send_notification(message)
                else:
                    if data['building'] != prevData['building'] or data['result'] != prevData['result']:
                        message = construct_message(data)
                        send_notification(message)

            save_json_file("%s.json" % (job), data)

        time.sleep(5)
