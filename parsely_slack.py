import requests
import datetime
from datetime import datetime as dt
from parsely.parsely import Parsely
import re


class ParselySlack(object):
    
    def __init__(self, apikey, secret):
        self._client = Parsely(apikey, secret=secret)
    
    def send(attachments=None, channel=None, username=None, text='default text'):
        ''' send a dict to slack properly '''
        # use the class objects if they exist
        slack_channel = channel or self.channel or "General"
        slack_username = username or self.username or "Parselybot"
        
        payload = {
            'channel': channel, 
            'username': 'Parselybot', 
            'text': 'Top 5 posts last 24 hours'}
            
        slack_attachments = attachments or self.attachments
        json_payload = {'payload': payload, 'attachments': slack_attachments}

        # take our json data and send it up
        try:
            requests.post(WEBHOOK_URL, data=json.dumps(json_payload))
            self.attachments = []
        except requests.exceptions.MissingSchema:
            print(
                'The webhook URL appears to be invalid. '
                'Are you sure you have the right webhook URL?')
                
    def build_attachments(entries, text):
        ''' takes list of Parsely meta objects and makes slack attachments out of them'''
        attachments = []
        intro_text = {'fallback': text, 
                   'pretext': text}
        attachments.append(intro_text)
        for entry in entries:
            meta = entry.__class__.__name__
            fields = [{
                'title': '{}: {}'.format(meta, entry.name), 
                'value': 'Hits: {}'.format(entry['_hits']), 
                'short':'false'
                }]
            if entry.url:
                temp_dict = {
                    'fallback': '<{}|{}>'.format(entry.url, 
                    entry['title']), 
                    'pretext':'<{}|{}>'.format(entry.url, entry.title)}
                
class AnalyticsHandler(object):
    ''' handles analytics parsing '''
    
    def __init__(self, client):
        self._client = client
    
    def parse(self, commands):
        options = {}
        ''' takes command (ex. author, John Flynn, monthtodate) and formats it'''
        # need a better way to do this, have a think later, this is gross
        
        if len(command) == 2:
            # sample command : /parsely, posts, monthtodate
        parsed['meta'] = command[0].strip()
        parsed['time'] = command[1].strip()
        
        
        elif len(command) == 3:
            # sample command: /parsely author, John Flynn, monthtodate
        parsed['meta'] = command[0].strip()
        parsed['value'] = command[1].strip()
        parsed['time'] = command[2].strip()
        
        
        # let's compute some sane things from these
        if parsed['time'] == 'monthtodate':
            options['days'] = dt.now().day
        
        elif parsed['time'] == 'weektodate':
            begin_date = dt.now() - datetime.timedelta(dt.now().weekday())
            options['days'] = begin_date.day
        
        elif parsed['time'] == 'today':
            options['days'] = '1'
            
        # have days, let's build query
        text = 'Top 10 {} in Last {} Days'.format(parsed['meta'], options['days'])
        post_list = self._client.analytics(aspect=parsed['meta'], **options)
        return post_list
        
        
        
        
            
            
    def 
        
        
            