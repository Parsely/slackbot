from flask import Flask
from flask_slack import Slack
from config import *
import parsely_slack
import threading
import urlparse
app = Flask(__name__)
    
slack = Slack(app)
slackbot = parsely_slack.ParselySlack(APIKEY, SHARED_SECRET)
@slack.command('parsely', token=SLACK_TOKEN, team_id=TEAM_ID, methods=['POST']) 
def parsely(**kwargs):
    text = kwargs.get('text')
    channel = kwargs.get('channel_name')
    commands = [word.strip() for word in text.strip().split(',')]
    if 'author' or 'post' or 'section' or 'tag' or 'referrers' in commands[0]:
        post_list, header_text = slackbot.parse(commands)
        if text == None:
            return slack.response("Sorry, didn't recognize that command!")
        if not post_list:
            return slack.response("Sorry, no posts found with that query!")
        attachments = slackbot.build_meta_attachments(post_list, header_text)
        return slack.response(text="", response_type="in_channel", attachments=attachments)
    else:
        return slack.response("Sorry, didn't recognize that command!")
    return slack.response("")

app.add_url_rule('/', view_func=slack.dispatch)


if __name__ == '__main__':
    app.run('0.0.0.0', 6000, debug=False, threaded=True)
