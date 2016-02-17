from __future__ import unicode_literals
import datetime as dt
'''
user can set alerts in command line as follows:

threshold: pageviews in last 5 minutes

channel: webhook

if pageview threshold goes above set threshold, notify channel.

'''

class SlackAlert(object):

    def __init__(self, slackbot):
        self.slackbot = slackbot
        # {url: timestamp} dict
        self.sent_notifications = {}

    def send_alert(self, attachments):
        ''' sends formatted JSON attachments to Slack '''
        for attachment in attachments:
            print attachment['url']

    def find_breaking_posts(self):
        ''' check if any URLs have exceeded pageview threshold '''
        time_period = lambda: None
        time_period.hours, time_period.minutes = None, 5
        top_posts = self.slackbot._client.realtime(aspect="posts", per=time_period, limit=100)

        # find breaking posts we haven't notified about
        breaking_posts = []
        now = dt.datetime.now()
        for post in top_posts:
            if post['views'] >= self.slackbot.config['threshold']:
               last_notified = self.sent_notifications.get(post['url'])
               if not last_notified or last_notified < now - dt.timedelta(hours=1):
                    self.sent_notifications[post['url']] = now
                    breaking_posts.append(post)
        return breaking_posts


def main():
    slack_alert = SlackAlert()
    last_check = None
    while True:
        if slack_alert.slackbot.config.get('threshold') > 0:
            now = dt.datetime.now()
            if not last_check or last_check < now - dt.timedelta(seconds=30):
                last_check = now
                slack_alert.find_breaking_posts()

