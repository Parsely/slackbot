from __future__ import unicode_literals
import argparse
import json
import requests
from config import *

# let's add some parser arguments
parser = argparse.ArgumentParser(description='call Parsely API and send top post results to Slack!')
parser.add_argument('--mention', nargs="*", help="usernames to mention")
parser.add_argument('--num', nargs=1, default=5, help="number of posts to return")
parser.add_argument('--no-thumbs', action='store_const', const="no_thumbs", help="don't get thumbnails")
args = parser.parse_args()
mentions = ''
for name in args.mention:
    mentions += "@{} ".format(name)
url = "https://api.parsely.com/v2/analytics/posts?apikey={}&page=1&limit={}&sort=_hits".format(APIKEY, args.num[0])
api_results = requests.get(url)
payload = {'channel': CHANNEL, "username": "Parselybot", "text": "Top 5 posts last 24 hours"}
attachments = []
intro_text =  {"fallback": "{}: Top {} Posts In 24 Hours".format(mentions, args.num[0]), 
                "pretext": "{}: Top {} Posts In 24 Hours".format(mentions, args.num[0])}
attachments.append(intro_text)
print api_results.json()
for entry in api_results.json()['data']:
    print entry['thumb_url_medium']
    fields = [{'title': "Author: {}".format(entry['author']), 
                'value': "Hits: {}".format(entry['_hits']), 
                'short':"false"}]
    temp_dict = {"fallback": "<{}|{}>".format(entry['url'], entry['title']), 
                    "pretext":"<{}|{}>".format(entry['url'], entry['title']),
                    'fields': fields}
    if not args.no_thumbs:
        temp_dict['thumb_url'] = entry['thumb_url_medium']
    attachments.append(temp_dict)
json_payload = {'payload': payload, 'attachments': attachments}


r = requests.post(WEBHOOK_URL, data=json.dumps(json_payload)) 
