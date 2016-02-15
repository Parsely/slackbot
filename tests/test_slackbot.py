import unittest

import parsely
from mock import MagicMock

from parsely_slackbot import slackbot


class ParselyTestCase(unittest.TestCase):

    def setUp(self):
        config = {
            'team_id': 'T090APE76',
            'slack_token': 'DcJRP8Lr9NRcjrQqAFoNQm2K',
            'apikey': 'elevatedtoday.com',
            'shared_secret': 'CzwEwFqgehL0w4sXDQ2Bbn6a5A1ixenjZlOiBNWz32A',
            'limit': 5
            }
        self.sample_slack_command = {"text": "posts, 55m",
                                     "command": "/parsely",
                                     "team_id": "T090APE76",
                                     "token": "DcJRP8Lr9NRcjrQqAFoNQm2K",
                                     "channel_name": "general"}
        # override the slackbot client to use our test API instance here
        self.meta_classes = ["Post", "Referrer", "Section", "Tag", "Author"]
        # just for convenience, have lower cased pluraled list of these
        self.metas = [("%ss" % meta).lower() for meta in self.meta_classes]
        self.slackbot = slackbot.SlackBot(config)

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
            assert isinstance(post_list[0], getattr(parsely.models,
                                                    self.meta_classes[index]))
            assert meta in text.lower()

    def test_build_post_attachment(self):
        parsed = {'meta': 'posts', 'time': '23h'}
        post_list = self.slackbot.realtime(parsed)[0]
        sample_attachment = self.slackbot.build_post_attachment(1, post_list[0])
        # meta attachment has no author
        assert "Author" in sample_attachment['fields'][0]['title']

    def test_build_meta_attachment(self):
        parsed = {'meta': 'sections', 'time': '23h'}
        post_list = self.slackbot.realtime(parsed)[0]
        sample_attachment = self.slackbot.build_meta_attachment(1, post_list[0])
        # meta attachment should have only one field, no author data or shares
        assert len(sample_attachment['fields']) == 1



if __name__ == '__main__':
    unittest.main()