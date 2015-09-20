from flask import Flask
from flask_slack import Slack
from config import *
app = Flask(__name__)

slack = Slack(app)

@slack.command('parsely', token=ACCESS_TOKEN, 
        team_id=None, methods]['POST']) 
def parsely(**kwargs):
    text = kwargs.get('text')

app.add_url_rule('/', view_func=slack.dispatch)


    if __name__ == '__main__':
            app.run()
