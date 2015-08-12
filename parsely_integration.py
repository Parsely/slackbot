import json
import requests
from config import *


url = "https://api.parsely.com/v2/analytics/posts?apikey={}&page=1&limit=5&sort=_hits".format(APIKEY)
api_results = requests.get(url)
payload = {'channel': CHANNEL, "username": "Parselybot", "text": "Top 5 posts last 24 hours"}
attachments = []
print api_results.json()
for entry in api_results.json()['data']:
    temp_dict = {"fallback": "Top Post: {}".format(entry['title']), "pretext":
                 "Top Post: {}".format(entry['title'])}


#r = requests.post(WEBHOOK_URL, data=json.dumps(payload))
