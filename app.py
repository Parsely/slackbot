from flask import Flask
from flask_slack import Slack
from config import *
import parsely_slack
import threading
import urlparse
app = Flask(__name__)

slack = Slack(app)
apikey = ""
secret = ""
slackbot = parsely_slack.ParselySlack(APIKEY, SHARED_SECRET)
team_id = urlparse.urlparse(WEBHOOK_URL).path.split('/')[2]
@slack.command('parsely', token=SLACK_TOKEN, team_id=team_id, methods=['POST']) 
def parsely(**kwargs):
    text = kwargs.get('text')
    commands = [word.strip() for word in text.strip().split(',')]
    if 'author' or 'post' or 'section' or 'tag' or 'referrers' in commands[0]:
        post_list, text = slackbot.parse(commands)
        if text == None:
            return slack.response("Sorry, didn't recognize that command!")
        attachments = slackbot.build_meta_attachments(post_list, text)
        slackbot.send(attachments, text=text)
    elif 'reports' in commands[0]:
        slackbot.reports.parse(commands)
    # elif shares:
    #     slackbot.shares(commands)
    # elif referrers:
    #     slackbot.referrers(commands)
    # elif realtime(commands):
    #     slackbot.realtime(commands)
    else:
        return slack.response("Sorry, didn't recognize that command!")
    return slack.response("")

app.add_url_rule('/', view_func=slack.dispatch)


if __name__ == '__main__':
    app.run('0.0.0.0', 6000, debug=False)
