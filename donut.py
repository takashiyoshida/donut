#!/usr/bin/env python

from datetime import datetime, timedelta
import json
import logging
import logging.handlers
from pprint import pprint
import sys
import time
import urllib
import urllib2

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
LOG_PATH = "donut_log"
LOG_MAX_BYTES = 1000000
LOG_BACKUP_COUNT = 20

#
# Initializes logger
#
def logging_init():
    f = logging.Formatter(fmt = LOG_FORMAT)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    fileHandler = logging.handlers.RotatingFileHandler(LOG_PATH, mode = 'a',
                                                       maxBytes = LOG_MAX_BYTES,
                                                       backupCount = LOG_BACKUP_COUNT)

    fileHandler.setFormatter(f)
    fileHandler.setLevel(logging.DEBUG)
    logger.addHandler(fileHandler)

    console = logging.StreamHandler()
    console.setFormatter(f)
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    return logger

#
# Loads data from a JSON file
#
def load_json_data(filename):
    json_data = None
    try:
        with open(filename, 'r') as infile:
            json_data = json.load(infile)
    except IOError as e:
        logging.critical(str(e))
    except ValueError as e:
        logging.critical("%s in %s" % (str(e), filename))
    return json_data


#
# Saves JSON data into a file
#
def save_json_data(filename, data):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)


#
# Fetches Jenkins CI job status
#
def get_jenkins_job_status(job):
    proxies = {}
    proxy_handler = urllib2.ProxyHandler(proxies)
    opener = urllib2.build_opener(proxy_handler)

    job_url = "%s/%s/%s" % (config['jenkins']['url'], job, config['jenkins']['suffix'])
    request = urllib2.Request(job_url)

    try:
        response = opener.open(request)
        data = json.loads(response.read())
        logging.info(data)
    except urllib2.HTTPError as e:
        logging.error("%s %s" % (str(e), job_url))
        data = None
    return data


#
# Returns true when the given job contains new status
#
def is_new_job_status(job, data):
    prevData = load_json_data("%s.json" % (job))
    if prevData == None:
        return True

    if data['fullDisplayName'] != prevData['fullDisplayName']:
        return True
    if data['building'] != prevData['building']:
        return True
    if data['result'] != prevData['result']:
        return True

    return False

#
# Creates a text message to be send as a notification
#
def create_message(data):
    completeTime = datetime.fromtimestamp(data['timestamp'] / 1000)
    if data['result'] == None and data['building'] == True:
        result = "In progress"
    else:
        result = data['result'].capitalize()
    return "%s:\n%s at %s" % (data['fullDisplayName'], result, completeTime)
    

def send_notification(message):
    payload = urllib.urlencode({'token': config['pushover']['api_token'],
                                'user': config['pushover']['user_key'],
                                'message': message, })
    request = urllib2.Request(config['pushover']['url'], data = payload,
                              headers = { 'Content-type': 'application/x-www-form-urlencoded' })

    proxies = {}
    if config['proxy']['enabled'] == "1":
        proxy_auth_url = "http://%s:%s@%s:%s" % (config['proxy']['username'],
                                                 config['proxy']['password'],
                                                 config['proxy']['url'],
                                                 config['proxy']['port'])
        proxies = {'http': proxy_auth_url, 'https': proxy_auth_url}

    proxy_handler = urllib2.ProxyHandler(proxies)
    opener = urllib2.build_opener(proxy_handler)

    try:
        response = opener.open(request)
        logging.info(response.geturl())
        logging.info(str(response.info()))
        logging.info(response.getcode())
        return response.getcode()
    except urllib2.URLError as e:
        logging.error(str(e))
    
    return -1


if __name__ == "__main__":
    logging_init()

    config = load_json_data('donut.json')
    if config == None:
        sys.exit(1)

    for job in config['jenkins']['jobs']:
        data = get_jenkins_job_status(job)
        if data:
            if is_new_job_status(job, data):
                message = create_message(data)
                if send_notification(message) == 200:
                    save_json_data("%s.json" % (job), data)
        else:
            logging.warning("Unable to retrieve job status for %s" % (job))
