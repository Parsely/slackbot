from flask import Flask
import flask_slack
import config
import parsely_slack
import threading
import urlparse
import json
app = Flask(__name__)

slack = flask_slack.Slack(app)
slackbot = parsely_slack.ParselySlack(config.APIKEY, config.SHARED_SECRET)
@slack.command('parsely', token=config.SLACK_TOKEN, team_id=config.TEAM_ID, methods=['POST'])
def parsely(text=None, channel=None, **kwargs):
    commands = [word.strip() for word in text.strip().split(',')]
    parsed_commands = slackbot.parse(commands)
    if not parsed_commands:
        return slack.response("Sorry, I didn't understand that query! Maybe try /parsely help?")
    post_list, header_text = slackbot.realtime(parsed_commands)
    if not header_text:
        return slack.response("Sorry, didn't recognize that command!")
    if not post_list:
        return slack.response("Sorry, no posts found with that query!")
    attachments = slackbot.build_meta_attachments(post_list, header_text)
    return slack.response(text="", response_type="in_channel", attachments=attachments)

app.add_url_rule('/', view_func=slack.dispatch)


if __name__ == '__main__':
    app.run('0.0.0.0', 6000, debug=False, threaded=True)
