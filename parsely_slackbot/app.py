import argparse
import flask_slack
from flask import Flask
import sys
import yaml
import alerts
import slackbot
import threading

def init(config_args):
    app = Flask(__name__)
    slack = flask_slack.Slack(app)
    config = slackbot.load_config(config_args.config)
    if not config:
        slackbot.save_config()
        print '''Looks like we can't find config.yaml-
        we've gone ahead and generated a sample one for you in the current directory.
        Please edit it according to the instructions in it and re-run parsely_slackbot!'''
        sys.exit()
    parsely_bot = slackbot.SlackBot(config)
    parsely_alert = alerts.SlackAlert(parsely_bot)
    # run this on a timer so that trending alerts don't happen the moment the bot is kicked off
    alerts_thread = threading.Timer(300.0, parsely_alert.run)
    alerts_thread.daemon = True
    alerts_thread.start()




    @slack.command('parsely', token=config['slack_token'], team_id=config['team_id'], methods=['POST'])
    def parsely(text=None, channel=None, **kwargs):
        parsed_commands = parsely_bot.parse(text)
        if not parsed_commands:
            return slack.response("Sorry, I didn't understand that query! Maybe try /parsely help?")
        if parsed_commands['meta'] == 'help':
            return slack.response(parsely_bot.help())
        post_list, header_text = parsely_bot.realtime(parsed_commands)
        if not header_text:
            return slack.response("Sorry, didn't recognize that command!")
        if not post_list:
            return slack.response("Sorry, no posts found with that query!")
        attachments = parsely_bot.build_meta_attachments(post_list, header_text)
        return slack.response(text="", response_type="in_channel", attachments=attachments)


    app.add_url_rule('/', view_func=slack.dispatch)
    app.run('0.0.0.0', config_args.port, debug=False, threaded=True)

def main():
    parser = argparse.ArgumentParser(description='Specify config options.')
    parser.add_argument('--config', dest='config', action='store', default='config.yaml')
    parser.add_argument('--port', dest='port', type=int, action='store', default=6000)
    args = parser.parse_args()
    init(args)

if __name__ == '__main__':
    main()
