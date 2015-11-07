from __future__ import unicode_literals
import requests
import datetime
import json
from datetime import datetime as dt
from parsely.parsely import Parsely
import re
from config import *

class ParselySlack(object):
    
    def __init__(self, apikey, secret):
        self._client = Parsely(apikey, secret=secret)
        self.analytics = AnalyticsHandler(self._client)
    
    def send(self, attachments=None, channel=None, username=None, text='default text'):
        ''' send a dict to slack properly '''
        # use the class objects if they exist
        slack_channel = channel or "general"
        slack_username = username or "Parselybot"
        
        payload = {
            'channel': channel, 
            'username': 'Parselybot', 
            'text': 'Top 5 posts last 24 hours'}
            
        slack_attachments = attachments or self.attachments
        json_payload = {'payload': payload, 'attachments': slack_attachments}

        # take our json data and send it up
        try:
            test_output = requests.post(WEBHOOK_URL, data=json.dumps(json_payload))
            print test_output.content
            self.attachments = []
        except requests.exceptions.MissingSchema:
            print(
                'The webhook URL appears to be invalid. '
                'Are you sure you have the right webhook URL?')
                
    def build_attachments(self, entries, text):
        ''' takes list of Parsely meta objects and makes slack attachments out of them'''
        attachments, temp_dict = [], {}
        intro_text = {'fallback': text, 
                   'pretext': text}
        attachments.append(intro_text)
        for entry in entries:
            meta = entry.__class__.__name__
            title = entry.url if meta == 'Post' else entry.name
            fields = [{
                    'value': 'Hits: {}'.format(entry.hits), 
                    'short':'false'
                    }]
            if meta == 'Post':
                fields[0]['title'] = 'Author: {}'.format(entry.author) 
                temp_dict = {
                    'fallback': '<{}|{}>'.format(entry.url, 
                    entry.title), 
                    'pretext':'<{}|{}>'.format(entry.url, entry.title)}
                shares = self._client.shares(post=entry.url)
                shares_dict = {
                    'title': 'shares', 'value': 'Twitter: {}, Facebook: {}'.format(
                        shares.twitter, shares.facebook),
                        'short': 'true'}
                fields.append(shares_dict)
            else:
                value_url_string = entry.name.replace(' ', '_')
                meta_url_string = meta + "s"
                url = 'http://dash.parsely.com/{}/{}/{}/'.format(APIKEY, meta_url_string.lower(), value_url_string)
                temp_dict = {
                    'fallback': '<{}|{}>'.format(url, entry.name), 
                    'pretext':'<{}|{}>'.format(url, entry.name)}
            temp_dict['fields'] = fields
            attachments.append(temp_dict)
        return attachments
                
class AnalyticsHandler(object):
    ''' handles analytics parsing '''
    
    def __init__(self, client):
        self._client = client
    
    def parse(self, commands):
        parsed, options = {}, {}
        ''' takes command (ex. author, John Flynn, monthtodate) and formats it'''
        # need a better way to do this, have a think later, this is gross
        
        if len(commands) == 2:
            # sample command : /parsely, posts, monthtodate
            parsed['meta'] = commands[0].strip()
            parsed['time'] = commands[1].strip()
        
        
        elif len(commands) == 3:
            # sample command: /parsely author, John Flynn, monthtodate
            parsed['meta'] = commands[0].strip()
            parsed['value'] = commands[1].strip()
            parsed['time'] = commands[2].strip()
        
        
        # let's compute some sane things from these
        if parsed['time'] == 'monthtodate':
            options['days'] = dt.now().day
        
        elif parsed['time'] == 'weektodate':
            begin_date = dt.now() - datetime.timedelta(dt.now().weekday())
            options['days'] = begin_date.day
        
        elif parsed['time'] == 'today':
            options['days'] = '1'
            
        # have days, let's build query
        post_list = self._client.analytics(aspect=parsed['meta'], **options)
        text = 'Top {} {} in Last {} Days'.format(str(len(post_list)), parsed['meta'], options['days'])
        return post_list, text
        
        
        
    
        
        
            