from __future__ import unicode_literals

from datetime import datetime as dt
import os
import yaml

import tzlocal
from parsely import parsely, models

def load_config(config_file):
    try:
        with open(config_file, 'r') as yaml_file:
            return yaml.load(yaml_file)
    except IOError:
        return None

def save_config(config_dict=None, config_file=None):
    if not config_dict and not os.path.exists('config.yaml'):
        # generate sample config.yaml
        with open('config.yaml', 'w') as yaml_file:
            yaml_file.write('''# replace values below with appropriate values as per documentation.
# Parsely API key and shared secret can be found in the dashboard in "Settings"->"API"
# Parsely apikey
apikey: example.com

#parsely shared_secret
shared_secret: abcdef12345

# slack team id- can find this at https://api.slack.com/methods/team.info/test
team_id: T12345

# Slack slash commands integration token
slack_token: abcdef12345

# posts to return for each query
limit: 5

# if threshold is greater than zero and webhook is set,
# the minimum pageviews in the last 5 minutes to trigger a trending alert
# to the listed channels
webhook_url: https://hooks.slack.com/services/T12345/example12345
threshold: 0
# channels:
# - "#general"
# - "#example"
''')



class TimePeriod(object):
    # little time period object to give to realtime client
    def __init__(self):
        self.time_str = None
        self.hours = None
        self.minutes = None

    @classmethod
    def from_str(cls, time):
        ''' takes a string like 1h, 2m, and returns a time_period object '''
        # let's compute some sane things from these
        time_period = cls()
        if time == 'today':
            time_period.hours = int(dt.now(tzlocal.get_localzone()).hour)
            return time_period

        if time.lower().endswith(('h', 'm')) and time[:-1].isdigit():
            qualifier, time = time[-1].lower(), int(time[:-1])
            if qualifier == 'h':
                time_period.time_str = 'Hour' if time == 1 else 'Hours'
                time_period.hours = time
            if qualifier == 'm':
                time_period.time_str = 'Minutes'
                time_period.minutes = time if time >= 5 else 5
            return time_period


class SlackBot(object):

    def __init__(self, config):
        self.config = config
        self._client = parsely.Parsely(self.config['apikey'], secret=config['shared_secret'])
        # pull default config params

    def build_meta_attachments(self, entries, text=''):
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
            return "http://dash.parsely.com/%s/find?url=%s" % (self.config['apikey'], entry.url)
        else:
            value_url_string = entry.name.replace(' ', '_')
            meta_url_string = "%ss" % (entry.__class__.__name__)
            if not isinstance(entry, models.Referrer):
                return 'http://dash.parsely.com/%s/%s/%s/' % (self.config['apikey'], meta_url_string.lower(), value_url_string)
            if entry.ref_type == 'direct':
                return 'http://dash.parsely.com/%s/referrers/' % (self.config['apikey'])
            if entry.ref_type == 'self':
                return 'http://dash.parsely.com/%s/%s/self/%s' % (self.config['apikey'], meta_url_string.lower(), value_url_string)
            else:
                return 'http://dash.parsely.com/%s/%s/%s/%s' % (self.config['apikey'], meta_url_string.lower(), entry.ref_type, value_url_string)

    def parse(self, commands):
        ''' takes command (ex. author, John Flynn, monthtodate) and formats it'''
        parsed = {}
        if "help" in commands or len(commands) == 0:
            return {'meta': 'help'}
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
        time_period = TimePeriod.from_str(parsed['time'])
        filter_string, time_string = "", ""
        if parsed.get('value') and parsed.get('filter_meta'):
            kwargs[parsed['filter_meta']] = parsed['value']
            filter_string = "For %s %s" % (parsed['filter_meta'], parsed['value'])
        post_limit = 50 if parsed.get('meta') == 'referrers' else self.config['limit']
        post_list = self._client.realtime(aspect=parsed['meta'], per=time_period, limit=post_limit, **kwargs)
        if parsed['meta'] == 'referrers':
            post_list.sort(key=lambda x: x.hits, reverse=True)
            # for some reason realtime referrers doesn't honor limit
            post_list = post_list[:self.config['limit']]
        if parsed['time'] == 'today':
            time_string = "Today"
        else:
            time_string = "In Last %s %s" % (parsed['time'][:-1], str(time_period.time_str))
        text = "Top %s %s %s %s" % (str(len(post_list)), parsed['meta'], filter_string, time_string)
        return post_list, text

    def help(self):
        # returns help commands
        return '''
Command syntax: /parsely meta, time
returns top metas for past minutes / hours

possible values for meta: posts, authors, sections, tags, referrers
possible values for time: a number followed by m for minutes or h for hours (ex. 30m, 12h). Max time value 24h

/parsely posts, 10m
Will return top posts for last 10 minutes

/parsely sections, 1h
Will return top sections for last hour

/parsely tags, today
Will return top tags for today

See all example commands: http://bit.ly/parsely_slack

'''



