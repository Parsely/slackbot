import unittest
import parsely_slack
import config
from parsely import parsely, models
class ParselyTestCase(unittest.TestCase):



    def setUp(self):

        config.TEAM_ID = 'T090APE76'
        config.TOKEN = 'DcJRP8Lr9NRcjrQqAFoNQm2K'
        config.APIKEY = 'elevatedtoday.com'
        config.SHARED_SECRET = 'CzwEwFqgehL0w4sXDQ2Bbn6a5A1ixenjZlOiBNWz32A'
        self.sample_slack_command = {"text": "posts, 55m",
                                     "command": "/parsely",
                                     "team_id": "T090APE76",
                                     "token": "DcJRP8Lr9NRcjrQqAFoNQm2K",
                                     "channel_name": "general"}
        # override the slackbot client to use our test API instance here
        self.meta_classes = ["Post", "Referrer", "Section", "Tag", "Author"]
        # just for convenience, have lower cased pluraled list of these
        self.metas = [("%ss" % meta).lower() for meta in self.meta_classes]
        self.slackbot = parsely_slack.ParselySlack(config.APIKEY, config.SHARED_SECRET)

    def test_parse(self):
        for meta in self.metas:
            command = "%s, 23h" % meta
            parsed_commands = self.slackbot.parse(command)
            assert parsed_commands['meta'] == meta
            if meta == 'posts':
                for filter_meta in ["Section", "Tag", "Author"]:
                    command = "posts, %s: News, 23h" % filter_meta
                    parsed_commands = self.slackbot.parse(command)
                    assert parsed_commands['filter_meta'] == filter_meta.lower()


    def test_realtime_call(self):
        for index, meta in enumerate(self.metas):
            parsed = {'meta': meta, 'time': '23h'}
            post_list, text = self.slackbot.realtime(parsed)
            assert isinstance(post_list[0], getattr(models, self.meta_classes[index])) and meta in text.lower()


    def test_build_post_attachment(self):
        parsed = {'meta': 'posts', 'time': '23h'}
        post_list, text = self.slackbot.realtime(parsed)
        sample_attachment = self.slackbot.build_post_attachment(1, post_list[0])
        # meta attachment has no author
        assert "Author" in sample_attachment['fields'][0]['title']

    def test_build_meta_attachment(self):
        parsed = {'meta': 'sections', 'time': '23h'}
        post_list, text = self.slackbot.realtime(parsed)
        sample_attachment = self.slackbot.build_meta_attachment(1, post_list[0])
        # meta attachment should have only one field, no author data or shares
        assert len(sample_attachment['fields']) == 1



if __name__ == '__main__':
    unittest.main()