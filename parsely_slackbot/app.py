from flask import Flask
import flask_slack
import config
import parsely_slack
import json

app = Flask(__name__)

slack = flask_slack.Slack(app)
slackbot = parsely_slack.ParselySlack(config.APIKEY, config.SHARED_SECRET)
@slack.command('parsely', token=config.SLACK_TOKEN, team_id=config.TEAM_ID, methods=['POST'])
def parsely(text=None, channel=None, **kwargs):
    parsed_commands = slackbot.parse(text)
    if not parsed_commands:
        return slack.response("Sorry, I didn't understand that query! Maybe try /parsely help?")
    if parsed_commands['meta'] == 'help':
        return slack.response(slackbot.help())
    post_list, header_text = slackbot.realtime(parsed_commands)
    if not header_text:
        return slack.response("Sorry, didn't recognize that command!")
    if not post_list:
        return slack.response("Sorry, no posts found with that query!")
    attachments = slackbot.build_meta_attachments(post_list, header_text)
    return slack.response(text="", response_type="in_channel", attachments=attachments)

app.add_url_rule('/', view_func=slack.dispatch)

def main():
    app.run('0.0.0.0', 6000, debug=False, threaded=True)
    
if __name__ == '__main__':
    main()