from __future__ import unicode_literals
import argparse
import json
import requests
import sys
from config import *

# let's add some parser arguments
parser = argparse.ArgumentParser(description='call Parsely API and send top post results to Slack!')
parser.add_argument('api_type', help='realtime or analytics') 
parser.add_argument('--mention', nargs='*', help='usernames to mention')
parser.add_argument('--limit', default=5, help='number of records to return')
parser.add_argument('--no-thumbs', action='store_const', const='no_thumbs', help="don't get thumbnails")
parser.add_argument('--shares', action='store_const', const='shares', 
                    help='get share counts for posts')
parser.add_argument('--time', default='1h', 
    help='Realtime only: number of minutes or hours for time period, up to 24h. Examples of valid values: 5m, 15m, 1h, 12h.')
parser.add_argument('--days', default=3, help='analytics only: number of days to count hits for (Default: 3)')
args = parser.parse_args()

mentions = ''
if args.mention:
    for name in args.mention:
        mentions += '@{} '.format(name)
url = ROOT_URL + '{}/posts?apikey={}&secret={}page=1&limit={}&sort=_hits&time={}&days={}'.format(
                    args.api_type, APIKEY, SHARED_SECRET, args.limit, args.time, args.days)
api_results = requests.get(url)
if api_results.json().get('success') is False:
    sys.exit("Couldn't get API results. Are you sure your shared secret is correct?")
# The 'text' field here appears to be unused when rich messaging is used as below,
# but is apparently still necessary
payload = {'channel': CHANNEL, 'username': 'Parselybot', 'text': 'Top 5 posts last 24 hours'}
attachments = []
if args.api_type == 'analytics':
    intro_text = {'fallback': '{}: Top {} Posts In Past {} Days'.format(mentions, args.limit, args.days), 
                   'pretext': '{}: Top {} Posts In Past {} Days'.format(mentions, args.limit, args.days)}
elif args.api_type == 'realtime':
    intro_text = {'fallback': '{}: Top {} Posts In Last {}'.format(mentions, args.limit, args.time), 
                   'pretext': '{}: Top {} Posts In Last {}'.format(mentions, args.limit, args.time)}
attachments.append(intro_text)
for entry in api_results.json()['data']:
    fields = [{'title': 'Author: {}'.format(entry['author']), 
                'value': 'Hits: {}'.format(entry['_hits']), 
                'short':'false'}]
    temp_dict = {'fallback': '<{}|{}>'.format(entry['url'], entry['title']), 
                    'pretext':'<{}|{}>'.format(entry['url'], entry['title'])}
    if not args.no_thumbs:
        temp_dict['thumb_url'] = entry['thumb_url_medium']
    if args.shares:
        shares_result = requests.get(
            'https://api.parsely.com/v2/shares/post/detail?apikey={}&url={}'.format(
                APIKEY, entry['url']))
        shares_dict = {'title': 'shares', 'value': 'Twitter: {}, Facebook: {}'.format(
                        shares_result.json()['data'][0]['tw'], shares_result.json()['data'][0]['fb']),
                        'short': 'true'}
        fields.append(shares_dict)
    temp_dict['fields'] = fields
    attachments.append(temp_dict)
json_payload = {'payload': payload, 'attachments': attachments}

# take our json data and send it up
try:
    requests.post(WEBHOOK_URL, data=json.dumps(json_payload))
except requests.exceptions.MissingSchema:
    print 'The webhook URL appears to be invalid. Are you sure you have the right webhook URL?'
    