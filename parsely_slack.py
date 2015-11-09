from __future__ import unicode_literals
import requests
import datetime
import json
from datetime import datetime as dt
from parsely.parsely import Parsely
import re
import requests
from config import *

class ParselySlack(object):
    
    def __init__(self, apikey, secret, username=None, password=None):
        self._client = Parsely(apikey, secret=secret)
        self.analytics = AnalyticsHandler(self._client)
        
        if username and password:
            login_data = {'email': username, 'password': password}
            url = "http://dash.parsely.com/login"
            self._session = requests.Session()
            self.dash_con = self._session.post(url, data=login_data)
    
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
                
    def build_meta_attachments(self, entries, text):
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
                if shares:
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
        
    def build_post_attachments(self, entry, text):
        ''' takes one post and builds an attachment for it '''
        pass
    
    def get_dash_link(url):
        ''' gets a dash link for the given URL '''
        
                
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
            
        if parsed['time'][-1].lower() == 'm' or parsed['time'][-1].lower() == 'h':
            return self.realtime(parsed)
        options['days'] = self.string_to_time(parsed['time'])
        # have days, let's build query
        post_list = self._client.analytics(aspect=parsed['meta'], **options)
        text = 'Top {} {} in Last {} Days'.format(str(len(post_list)), parsed['meta'], options['days'])
        return post_list, text
        
    def string_to_time(self, time):
        # turn a string like monthtodate, weektodate, into a time
        # let's compute some sane things from these
        if time == 'monthtodate':
            days = dt.now().day
        
        elif time == 'weektodate':
            begin_date = dt.now() - datetime.timedelta(dt.now().weekday())
            days = begin_date.day
        
        elif time == 'today':
            days = '1'
            
        return days
        
    def realtime(self, parsed):
        # takes parsed commands and returns a post_list for realtime
        # need a little function here we can add attributes to
        time_period = lambda: None
        time_period.hours = []
        if parsed['time'][-1].lower() == 'h':
            time_period.hours = int(parsed['time'][:2])
            time_period.time_str = 'Hours'
        elif parsed['time'][-1].lower() == 'm':
            time_period.minutes = int(parsed['time'][:2])
            time_period.time_str = 'Minutes'
        post_list = self._client.realtime(aspect=parsed['meta'], per=time_period)
        print parsed['meta']
        print post_list
        text = 'Top {} {} in Last {} {}'.format(str(len(post_list)), parsed['meta'], parsed['time'][:2], str(time_period.time_str))
        return post_list, text
        
        
    def post_detail(self, post, parsed):
        # takes a post and some parsed commands and returns post detail
        
    
        
        
            