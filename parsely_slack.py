from __future__ import unicode_literals
import requests
import calendar
import datetime
import json
import pytz
import tzlocal
from datetime import datetime as dt
from parsely.parsely import Parsely
import re
import requests
from config import *

class ParselySlack(object):
    
    def __init__(self, apikey, secret, username=None, password=None):
        self._client = Parsely(apikey, secret=secret)
        self.analytics = AnalyticsHandler(self._client)
        # pull default config params
        self.config = {'days': DAYS, 'limit': LIMIT}
    
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
        for index, entry in enumerate(entries):
            meta = entry.__class__.__name__
            if meta == 'Post':
                attachment = self.build_post_attachment(index, entry)
                if len(entries) == 1:
                    visitors_dict = {
                        'title': 'visitors',
                        'value': '{}'.format(entry.visitors),
                        'short': 'true'}
                    res_list.append(visitors_dict)
                    attachment['fields'].append(visitors_dict)
                attachments.append(attachment)
            else:
                attachments.append(self.build_meta_attachment(index, entry))
        return attachments
        
        
    def build_post_attachment(self, index, entry):
        ''' takes one post and builds an attachment for it '''
        title = str(index+1) + '. ' + entry.title
        dash_link = self.get_dash_link(entry.url)
        res_list = [{
                'value': 'Hits: {}'.format(entry.hits), 
                'short':'false'
                }]
        res_list[0]['title'] = 'Author: {}'.format(entry.author) 
        temp_dict = {
            'fallback': '<{}|{}>'.format(dash_link, 
            title), 
            'pretext':'<{}|{}>'.format(dash_link, title)}
        shares = self._client.shares(post=entry.url)
        temp_dict['thumb_url'] = entry.thumb_url_medium
        if shares:
            shares_dict = {
                'title': 'shares', 'value': 'Twitter: {}, Facebook: {}'.format(
                    shares.twitter, shares.facebook),
                    'short': 'true'}
            res_list.append(shares_dict)
        temp_dict['fields'] = res_list
        return temp_dict
            
    def build_meta_attachment(self, index, entry):
        title = str(index+1) + '. ' + entry.name
        meta = entry.__class__.__name__
        value_url_string = entry.name.replace(' ', '_')
        meta_url_string = meta + "s"
        url = 'http://dash.parsely.com/{}/{}/{}/'.format(APIKEY, meta_url_string.lower(), value_url_string)
        fields = [{
                'value': 'Hits: {}'.format(entry.hits), 
                'short':'false'
                }]
        temp_dict = {
            'fallback': '<{}|{}>'.format(url, entry.name), 
            'pretext':'<{}|{}>'.format(url, entry.name)}
        temp_dict['fields'] = fields
        return temp_dict
    
    def get_dash_link(self, url):
        ''' gets a dash link for the given URL '''
        return "http://dash.parsely.com/{}/find?url={}".format(APIKEY, url)
        
                
class AnalyticsHandler(object):
    ''' handles analytics parsing '''
    
    def __init__(self, client):
        self._client = client
    
    def parse(self, commands):
        parsed, options = {}, {}
        options['limit'] = LIMIT
        ''' takes command (ex. author, John Flynn, monthtodate) and formats it'''
        # need a better way to do this, have a think later, this is gross
        
        metas = ["posts", "tags", "sections", "authors"]
        metas_detail = ["tag", "section", "author"]
        if commands[0] in metas:
            # sample command : /parsely, posts, monthtodate
            parsed['meta'] = commands[0].strip()
            parsed['time'] = commands[1].strip()
            if parsed['meta'] == 'post':
                parsed['value'] = commands[1].strip()
        
        elif commands[0] in metas_detail:
            # sample command: /parsely author, John Flynn, monthtodate
            parsed['meta'] = commands[0].strip()
            parsed['value'] = commands[1].strip()
            parsed['time'] = commands[2].strip()
            
        else:
            return None, None
         
        if not parsed['time']:
            # give default of last hour
            parsed['time'] = '1h'
        if (parsed['time'][-1].lower() == 'm' or 
                parsed['time'][-1].lower() == 'h' or 
                parsed['time'] == 'today'):
            return self.realtime(parsed, **options)
        options['days'] = self.string_to_time(parsed['time'])
        # have days, let's build query
        if parsed['meta'] == 'post':
            post = self.post_detail(parsed, **options)
            text = "Detailed Look"
            return post, text
        elif parsed['meta'][-1] != 's':
            text = "Detailed Look"
            post = self.meta_detail(parsed, **options)
            return post, text
            
        post_list = self._client.analytics(aspect=parsed['meta'], **options)
        text = 'Top {} {} in Last {} Days'.format(str(len(post_list)), parsed['meta'], options['days'])
        if (parsed['meta'] == 'posts'):
            self.last_post_list = post_list
        return post_list, text
        
    def string_to_time(self, time):
        # turn a string like monthtodate, weektodate, into a time
        # let's compute some sane things from these
        time_period = lambda: None
        time_period.hours = []
        if time == 'monthtodate':
            res = dt.now(tzlocal.get_localzone()).day
        
        elif time == 'weektodate':
            begin_date = dt.now(tzlocal.get_localzone()).weekday()
            res = begin_date + 1
        
        elif time == 'today':
            res = dt.now(tzlocal.get_localzone()).hour
            time_period.hours = int(res)
            res = time_period
            
        elif time[-1].lower() == 'h':
            time_period.hours = int(time[:-1])
            time_period.time_str = 'Hours'
            res = time_period
                
        elif time[-1].lower() == 'm':
            time_period.minutes = int(time[:-1])
            time_period.time_str = 'Minutes'
            res = time_period
            
        elif time == 'yesterday':
            res = '1'
            
        else:
            res = '1'
        return res
        
    def realtime(self, parsed, **kwargs):
        # takes parsed commands and returns a post_list for realtime
        # need a little function here we can add attributes to
        time_period = self.string_to_time(parsed['time'])
        post_list = self._client.realtime(aspect=parsed['meta'], per=time_period, **kwargs)
        if parsed['time'] == 'today':
            text = 'Top {} {} Today'.format(str(len(post_list)), parsed['meta'])
        else:
            text = 'Top {} {} in Last {} {}'.format(str(len(post_list)), parsed['meta'], parsed['time'][:-1], str(time_period.time_str))
        return post_list, text
        
        
        
        
    def post_detail(self, parsed, **kwargs):
        # takes a post and some parsed commands and returns post detail
        if 'http' in parsed.get('value'):
            post = [self._client.post_detail(post=parsed['value'], **options)]
        else:
            post_num = int(parsed['value'])
            post = [self._client.post_detail(post=self.last_post_list[post_num-1], **kwargs)]
        return post
        
            
            
    
    def spark_string(ints, fit_min=False):
        min_range = 0
        if fit_min:
            min_range = min(ints)
    
        step_range = max(ints) - min_range
        step = ((step_range) / float(len(ticks) - 1)) or 1
        return u''.join(ticks[int(round((i - min_range) / step))] for i in ints)
        
    
        
        
            