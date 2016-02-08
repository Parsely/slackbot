Parsely Slackbot
==================

Parsely slackbot is an open-source slack custom integration that uses the Parsely
API to allow realtime Slackalytics in your Slack instance!

Installation
----------------
1. Head over to the custom integrations section of your Slack team and add a
"Slash Commands" integration.
2. In the "command" section, put "/parsely" (without quotes..
3. in the "URL" field, enter the URL your slackbot will be running on (Make sure
to specify the port if necessary in the style of http://slackbot.com:6000.
4. The rest of the fields can be left as their defaults (though feel free to change
the name and portrait for the bot..
5. on the server pointed to in #3, clone this repository.
6. copy "sample.config.py" to "config.py" and replace all the sample values
with values from your Parsely and Slack instances.
7. install the dependencies needed for the app with:

```
pip install -r requirements.txt

```

Then run "python app.py" and your slackbot will be ready to receive commands!


Note: The lightweight server shipped with Flask will work for
small and mid-sized teams. For larger teams, you might want to look into a more
robust WSGI server like gunicorn in the event that you experience stability
issues.

Usage
-------
/parsely <meta>, <time>

examples:

/parsely posts, 10m returns top posts for last 10 minutes
/parsely sections, 1h returns top sections for last hour
/parsely tags, today returns top tags for today

for posts, you can further filter posts by specifying the meta to filter on with
a colon.

examples:

/parsely posts, section: News, 1h returns top posts in the News section for the past hour
/parsely posts, tag: article, 25m returns top posts with the article tag for the past 25 minutes

please note that the metas are case sensitive and must be written exactly as they appear in the dashboard.

