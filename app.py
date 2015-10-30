from flask import Flask
from flask_slack import Slack
from config import *
app = Flask(__name__)

slack = Slack(app)

@slack.command('parsely', 'DcJRP8Lr9NRcjrQqAFoNQm2K', 'T090APE76',
                ['POST']) 
def parsely(**kwargs):
    text = kwargs.get('text')
    print text

app.add_url_rule('/', view_func=slack.dispatch)


if __name__ == '__main__':
        app.run('0.0.0.0', 6000)
