Parsely Slackbot
==================

Parsely slackbot is an open-source slack custom integration that uses the Parsely
API to allow realtime Slackalytics in your Slack instance!

Server set up
----------------

You'll need to run the slackbot on a server. 

Run: 

```
pip install parsely-slackbot
```

and then run:

```
parsely_slackbot
```

The bot will generate a sample config.yaml for you. See a `sample here 
<https://github.com/Parsely/slackbot/blob/master/parsely_slackbot/sample_conf.yaml/>`_. Edit with your Site ID and API shared secret for the account you want to show in the channel. You can find these `here <https://dash.parsely.com/to/settings/api/>`_. You will need the Slack team ID from your channel and the Slack token from the set up below.

Slack Channel Set Up
------------------------

1. In your channel settings, select "Customize Slack." Choose "Configure Apps" --> "Custom Integrations"  
2. Add a "Slash Commands" integration
3. In the "command" section, enter "/parsely" (without quotes)
4. In the "URL" field, enter the URL your slackbot will be running on, created in the Server Set Up step. Make sure to specify the port in the style of http://EXAMPLE.com:6000. (The default port is 6000 for the slackbot)
5. The rest of the fields can be left as their defaults. You can also upload the `Parse.ly logo <http://www.parsely.com/static/img/parsely-green-leaf-m.png>`_. 


Note: The lightweight server shipped with Flask has worked quite well in testing for small and mid-sized teams. For larger teams (and as a best practice in general), you might want to look into a more robust WSGI server like gunicorn so as not to experience stability issues.

Usage
-------
| Command syntax:
| /parsely meta, time
| 
| meta = posts, authors, sections, tags, referrers 
| time = Xm, Yh, today. Max of 24h. 
| 
| Sample commands:
| 
| /parsely posts, 10m 
| Will return the top posts in the last 10 minutes
| 
| /parsely sections, 1h 
| Will return the top sections in the last hour
| 
| /parsely tags, today 
| Will return the top tags for today
| 
| Filtering
| For use with "posts" add a colon to filter to a specific author, section, tag or referrer
| 
| /parsely posts, section: News, 1h 
| Will return top posts in the News section for the past hour
| 
| /parsely posts, tag: obama, 25m 
| Will return top posts with the tag "obama" for the past 25 minutes
| 
| Please note that the filters are case sensitive and must be written exactly as they appear in the dashboard.
