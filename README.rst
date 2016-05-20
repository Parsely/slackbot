Parsely Slackbot
==================

Parsely slackbot is an open-source slack custom integration that uses the Parsely
API to allow realtime Slackalytics in your Slack instance!

Server Set Up
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

Pageview Threshold Notification
---------------------------------

The slackbot has the ability to poll Parsely's realtime data endpoint and automatically alert you if any urls break a pageview threshold that you can set. Here's how to set that up:

1. Go to the same custom integrations page as in the steps above.
2. At that page, click "Add Incoming Webhook". 
3. Select a channel you want the bot to send to (don't worry about being too choosy- the bot can override this later in its settings) and click "Add Webhook Integration". Once the webhook is created, make sure to copy the webhook url slack gives you. (Not required, though highly encouraged, is to name the integration and give it a new logo- you can use the logo provided above!)
4. in your config.yaml, change the parameter "webhook_url" to the webhook URL Slack gave you in the previous step. Also set the "threshold" parameter to the minimum number of pageviews a post must have in the past 5 minutes to trigger the trending alert.
5. under the "channels" list, add every channel you'd like the bot to send alerts to.

save the config.yaml, restart the bot, and you're all set! 

