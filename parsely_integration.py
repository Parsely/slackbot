from __future__ import unicode_literals
import argparse
import json
import requests
from config import *

# let's add some parser arguments
parser = argparse.ArgumentParser(description='call Parsely API and send top post results to Slack!')
parser.add_argument('--mention', nargs="*", help="usernames to mention")
parser.add_argument('--num', default=5, help="number of posts to return")
parser.add_argument('--no-thumbs', action='store_const', const="no_thumbs", help="don't get thumbnails")
parser.add_argument('--shares', action='store_const', const="shares", 
                    help="get share counts for posts")
args = parser.parse_args()

mentions = ''
if args.mention:
    for name in args.mention:
        mentions += "@{} ".format(name)
url = "https://api.parsely.com/v2/analytics/posts?apikey={}&page=1&limit={}&sort=_hits".format(APIKEY, args.num)
print url
api_results = requests.get(url)
# The "text" field here appears to be unused when rich messaging is used as below,
# but is apparently still necessary
payload = {'channel': CHANNEL, "username": "Parselybot", "text": "Top 5 posts last 24 hours"}
attachments = []
intro_text =  {"fallback": "{}: Top {} Posts In Past 1 Days".format(mentions, args.num), 
                "pretext": "{}: Top {} Posts In 24 Hours".format(mentions, args.num)}
attachments.append(intro_text)
for entry in api_results.json()['data']:
    fields = [{'title': "Author: {}".format(entry['author']), 
                'value': "Hits: {}".format(entry['_hits']), 
                'short':"false"}]
    temp_dict = {"fallback": "<{}|{}>".format(entry['url'], entry['title']), 
                    "pretext":"<{}|{}>".format(entry['url'], entry['title'])}
    if not args.no_thumbs:
        temp_dict['thumb_url'] = entry['thumb_url_medium']
    if args.shares:
        shares_result = requests.get(
            'https://api.parsely.com/v2/shares/post/detail?apikey={}&url={}'.format(
                APIKEY, entry['url']))
        shares_dict = {'title': "shares", "value": "Twitter: {}, Facebook: {}".format(
                        shares_result.json()['data'][0]['tw'], shares_result.json()['data'][0]['fb']),
                        'short': "true"}
        fields.append(shares_dict)
    temp_dict['fields'] = fields
    attachments.append(temp_dict)
json_payload = {'payload': payload, 'attachments': attachments}

# take our json data and send it up
try:
    requests.post(WEBHOOK_URL, data=json.dumps(json_payload))
except requests.exceptions.MissingSchema:
    print "The webhook URL appears to be invalid. Are you sure you have the right webhook URL?"