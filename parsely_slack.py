from __future__ import unicode_literals
import calendar
import datetime
from datetime import datetime as dt
import json
import pytz
import requests
import tzlocal

from parsely import parsely, models
import config

class TimePeriod(object):
    # little time period object to give to realtime client
    def __init__(self):
        self.time_str = None
        self.hours = None
        self.minutes = None

def parse_time(time):
    ''' takes a string like 1h, 2m, and returns a time_period object '''
    # let's compute some sane things from these
    time_period = TimePeriod()
    if time == 'today':
        time_period.hours = int(dt.now(tzlocal.get_localzone()).hour)
        return time_period

    if time[-1].lower() == 'h' or 'm' and time[:-1].isdigit():
        qualifier, time = time[-1].lower(), int(time[:-1])
        if qualifier == 'h':
            time_period.time_str = 'Hour' if time == 1 else 'Hours'
            time_period.hours = time
        if qualifier == 'm':
            time_period.time_str = 'Minutes'
            time_period.minutes = time if time >= 5 else 5
        return time_period

    return None

class ParselySlack(object):

    def __init__(self, apikey, secret, username=None, password=None):
        self._client = parsely.Parsely(apikey, secret=secret)
        # pull default config params

    def build_meta_attachments(self, entries, text):
        ''' takes list of Parsely meta objects and makes slack attachments out of them '''
        attachments = [{'fallback': text, 'pretext': text}]
        for index, entry in enumerate(entries):
            if isinstance(entry, models.Post):
                attachment = self.build_post_attachment(index, entry)
                attachments.append(attachment)
            else:
                attachments.append(self.build_meta_attachment(index, entry))
        return attachments

    def build_post_attachment(self, index, entry):
        ''' takes one post and builds an attachment for it '''
        title = "%s. %s" % (str(index+1), entry.title)
        dash_link = self.get_dash_link(entry)
        res_list = [{
                'value': 'Hits: %s' % entry.hits,
                'short':'false',
                'title': 'Author: %s' % entry.author
                }]
        attachment = {
            'fallback': '<%s|%s>' % (dash_link, title),
            'pretext':'<%s|%s>' % (dash_link, title),
            'thumb_url': entry.thumb_url_medium
            }
        shares = self._client.shares(post=entry.url)
        shares_dict = {
            'title': 'shares',
            'value': 'Twitter: %s, Facebook: %s' % (shares.twitter, shares.facebook),
            'short': 'true'}
        res_list.append(shares_dict)
        if entry.visitors:
            visitors_dict = {
                'title': 'visitors',
                'value': '%s' % entry.visitors,
                'short': 'true'}
            res_list.append(visitors_dict)
        attachment['fields'] = res_list
        return attachment

    def build_meta_attachment(self, index, entry):
        fields = [{
                'value': 'Hits: %s' % entry.hits,
                'short':'false'
                }]
        try:
            fields[0]['value'] += "\nReferrer Type: %s" % entry.ref_type
        except AttributeError:
            pass
        url = self.get_dash_link(entry)
        attachment = {
            'fallback': '<{}|{}>'.format(url, entry.name),
            'pretext':'<{}|{}>'.format(url, entry.name)}
        attachment['fields'] = fields
        return attachment

    def get_dash_link(self, entry):
        ''' gets a dash link for the given Parsely model object '''
        if isinstance(entry, models.Post):
            return "http://dash.parsely.com/%s/find?url=%s" % (config.APIKEY, entry.url)
        else:
            value_url_string = entry.name.replace(' ', '_')
            meta_url_string = "%ss" % (entry.__class__.__name__)
            if not isinstance(entry, models.Referrer):
                return 'http://dash.parsely.com/%s/%s/%s/' % (config.APIKEY, meta_url_string.lower(), value_url_string)
            if entry.ref_type == 'direct':
                return 'http://dash.parsely.com/%s/referrers/' % (config.APIKEY)
            if entry.ref_type == 'self':
                return 'http://dash.parsely.com/%s/%s/self/%s' % (config.APIKEY, meta_url_string.lower(), value_url_string)
            else:
                return 'http://dash.parsely.com/%s/%s/%s/%s' % (config.APIKEY, meta_url_string.lower(), entry.ref_type, value_url_string)



    def parse(self, commands):
        ''' takes command (ex. author, John Flynn, monthtodate) and formats it'''
        parsed = {}
        split_commands = commands.strip().split(',')
        if len(split_commands) < 2:
            return None
        command = split_commands[0]
        params = [param.strip() for param in split_commands[1:]]
        metas = ["posts", "tags", "sections", "authors", "referrers"]
        metas_detail = ["tag", "section", "author"]
        if not command in metas:
            return None
        elif command in metas:
            # sample command : /parsely, posts, 10m
            if len(split_commands) == 1:
                if not parsed.get('time'):
                # give default of last hour
                    parsed['time'] = '1h'
                parsed['meta'] = command.strip()
            if len(split_commands) == 2:
                parsed['meta'] = command.strip()
                parsed['time'] = params[0].strip()
            if len(split_commands) == 3:
                parsed['meta'] = command.strip()
                if params[0].split(':')[0].lower() in metas_detail:
                    meta_filter = [param.strip() for param in params[0].split(':')]
                    parsed['filter_meta'] = meta_filter[0].lower()
                    parsed['value'] = meta_filter[1]
                parsed['time'] = params[1].strip()

        else:
            return None

        return parsed


    def realtime(self, parsed, **kwargs):
        # takes parsed commands and returns a post_list for realtime
        time_period = parse_time(parsed['time'])
        filter_string, time_string = "", ""
        if parsed.get('value') and parsed.get('filter_meta'):
            kwargs[parsed['filter_meta']] = parsed['value']
            filter_string = "For %s %s" % (parsed['filter_meta'], parsed['value'])
        post_limit = 50 if parsed.get('meta') == 'referrers' else config.LIMIT
        post_list = self._client.realtime(aspect=parsed['meta'], per=time_period, limit=post_limit, **kwargs)
        if parsed['meta'] == 'referrers':
            post_list.sort(key=lambda x: x.hits, reverse=True)
            # for some reason realtime referrers doesn't honor limit
            post_list = post_list[:config.LIMIT]
        if parsed['time'] == 'today':
            time_string = "Today"
        else:
            time_string = "In Last %s %s" % (parsed['time'][:-1], str(time_period.time_str))
        text = "Top %s %s %s %s" % (str(len(post_list)), parsed['meta'], filter_string, time_string)
        return post_list, text



