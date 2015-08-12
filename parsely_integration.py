from __future__ import unicode_literals
import json
import requests
from config import *


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
