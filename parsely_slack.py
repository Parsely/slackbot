from __future__ import unicode_literals
import calendar
import datetime
from datetime import datetime as dt
import json
import pytz
import requests
import tzlocal

from parsely.parsely import Parsely
from config import *


def string_to_time(time):
    # turn a string like monthtodate, weektodate, into a time
    # let's compute some sane things from these
    time_period = lambda: None
    #python-parsely needs hours set, even if it's blank, or it errors out
    time_period.hours = []
    if time == 'today':
        time_period.hours = int(dt.now(tzlocal.get_localzone()).hour)
        res = time_period
        
    elif time[-1].lower() == 'h':
        time_period.hours = int(time[:-1])
        time_period.time_str = 'Hour' if int(time_period.hours) == 1 else 'Hours'
        res = time_period
            
    elif time[-1].lower() == 'm':
        time_period.minutes = int(time[:-1])
        if time_period.minutes < 5:
            # can't do less than 5 minutes, just set to 5
            time_period.minutes = 5
        time_period.time_str = 'Minutes'
        res = time_period
        
    elif time[-1].lower() == 'd':
        if time[:-1].isdigit():
            res = time[:-1]
        
    elif time == 'yesterday':
        res = '1'
        
    elif time.isdigit():
        res = time
        
    else:
        res = '1'
    
    return res
        
class ParselySlack(object):
    
    def __init__(self, apikey, secret, username=None, password=None):
        self._client = Parsely(apikey, secret=secret)
        # pull default config params
        self.config = {'limit': LIMIT} 
                
    def build_meta_attachments(self, entries, text):
        ''' takes list of Parsely meta objects and makes slack attachments out of them'''
        attachments = [{'fallback': text, 'pretext': text}]
        for index, entry in enumerate(entries):
            if entry.__class__.__name__ == 'Post':
                attachment = self.build_post_attachment(index, entry)
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
                'short':'false',
                'title': 'Author: {}'.format(entry.author)
                }]
        attachment = {
            'fallback': '<{}|{}>'.format(dash_link, title), 
            'pretext':'<{}|{}>'.format(dash_link, title),
            'thumb_url': entry.thumb_url_medium
            }
        shares = self._client.shares(post=entry.url)
        shares_dict = {
            'title': 'shares', 'value': 'Twitter: {}, Facebook: {}'.format(
                shares.twitter, shares.facebook),
                'short': 'true'}
        res_list.append(shares_dict)
        if entry.visitors:
            visitors_dict = {
                'title': 'visitors',
                'value': '{}'.format(entry.visitors),
                'short': 'true'}
            res_list.append(visitors_dict)
        attachment['fields'] = res_list
        return attachment
            
    def build_meta_attachment(self, index, entry):
        title = str(index+1) + '. ' + entry.name
        value_url_string = entry.name.replace(' ', '_')
        meta_url_string = "{}s".format(entry.__class__.__name__)
        url = 'http://dash.parsely.com/{}/{}/{}/'.format(APIKEY, meta_url_string.lower(), value_url_string)
        fields = [{
                'value': 'Hits: {}'.format(entry.hits), 
                'short':'false'
                }]
        try:
            fields[0]['value'] += "\nReferrer Type: {}".format(entry.ref_type)
            if entry.ref_type == 'direct':
                url = 'http://dash.parsely.com/{}/referrers/'.format(APIKEY)
            if entry.ref_type == 'self':
                url = 'http://dash.parsely.com/{}/{}/internal/{}'.format(APIKEY, meta_url_string.lower(), value_url_string)
            else:
                url = 'http://dash.parsely.com/{}/{}/{}/{}'.format(APIKEY, meta_url_string.lower(), entry.ref_type, value_url_string)
        except AttributeError:
            pass
        attachment = {
            'fallback': '<{}|{}>'.format(url, entry.name), 
            'pretext':'<{}|{}>'.format(url, entry.name)}
        attachment['fields'] = fields
        return attachment
    
    def get_dash_link(self, url):
        ''' gets a dash link for the given URL '''
        return "http://dash.parsely.com/{}/find?url={}".format(APIKEY, url)
        
    def parse(self, commands):
        parsed, options = {}, {}
        options['limit'] = LIMIT
        ''' takes command (ex. author, John Flynn, monthtodate) and formats it'''
        metas = ["posts", "tags", "sections", "authors"]
        metas_detail = ["tag", "section", "author"]
        if not commands[0] in metas:
            return None, None
        if commands[0] == 'referrers':
            parsed['meta'] = commands[0]
            parsed['time'] = commands[1]
        elif commands[0] in metas:
            # sample command : /parsely, posts, monthtodate
            if len(commands) == 1:
                if not parsed.get('time'):
                # give default of last hour
                    parsed['time'] = '1h'
                parsed['meta'] = commands[0].strip()
            if len(commands) == 2:
                parsed['meta'] = commands[0].strip()
                parsed['time'] = commands[1].strip()
            if len(commands) == 3:
                parsed['meta'] = commands[0].strip()
                parsed['value'] = commands[1].strip() if commands[1] in metas_detail else None
                parsed['time'] = commands[2].strip()
        
        else:
            return None, None

        return self.realtime(parsed, **options)
        
        
    def realtime(self, parsed, **kwargs):
        # takes parsed commands and returns a post_list for realtime
        time_period = string_to_time(parsed['time'])
        filter_string, time_string = "", ""
        if parsed.get('value'):
            filter_meta, value = [x.strip() for x in parsed['value'].split(':')]
            kwargs[filter_meta] = value
            filter_string = "For {} {}".format(filter_meta, value)
        post_list = self._client.realtime(aspect=parsed['meta'], per=time_period, **kwargs)
        if parsed['meta'] == 'referrers':
            post_list.sort(key=lambda x: x.hits, reverse=True)
            # for some reason realtime referrers doesn't honor limit
            post_list = post_list[:LIMIT]
        if parsed['time'] == 'today':
            time_string = "Today"
        else:
            time_string = "In Last {} {}".format(parsed['time'][:-1], str(time_period.time_str))
        text = "Top {} {} {} {}".format(str(len(post_list)), parsed['meta'], filter_string, time_string)
        return post_list, text
        
        
        
        