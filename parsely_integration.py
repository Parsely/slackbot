from __future__ import unicode_literals
import argparse
import json
import requests
from config import *

# let's add some parser arguments
parser = argparse.ArgumentParser(description='call Parsely API and send top post results to Slack!'
parser.add_argument('--mention', nargs="*", help="usernames to mention")
parser.add_argument('--num', nargs="*", type=int, default=5, help="number of posts to return")
args = parser.argparse()
print args
url = "https://api.parsely.com/v2/analytics/posts?apikey={}&page=1&limit=5&sort=_hits".format(APIKEY)
api_results = requests.get(url)
payload = {'channel': CHANNEL, "username": "Parselybot", "text": "Top 5 posts last 24 hours"}
attachments = []
print api_results.json()
for entry in api_results.json()['data']:
    fields = [{'title': "Author: {}".format(entry['author']), 
    'value': "Hits: {}".format(entry['_hits']), 'short':'false'}]
    temp_dict = {"fallback": "<{}|{}>".format(entry['url'], entry['title']), "pretext":
                 "<{}|{}>".format(entry['url'], entry['title']), 'fields': fields}
    attachments.append(temp_dict)
json_payload = {'payload': payload, 'attachments': attachments}


r = requests.post(WEBHOOK_URL, data=json.dumps(json_payload)) 
