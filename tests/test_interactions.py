import os
import sys

from flask.app import Flask

sys.path.append("..")

from unittest import TestCase

from bot import SlackBot
from config import config
from endpoints._flask import Interactions

from tests.test_flask import FlaskAppWrapper


class TestInteractions(TestCase):
    def setUp(self):
        config.load_env()
        self.bot = SlackBot()
        self.flask = FlaskAppWrapper(Flask(__name__))
        self.client = self.flask.app.test_client()
        self.test_id = os.environ["TEST_ID"]

    def test_interactions(self):
        interactions = Interactions(self.bot)
        self.flask.add_endpoint(
            endpoint="/interactions", endpoint_name="interactions", handler=interactions.handler, methods=["POST"]
        )
        response = self.client.post(
            "interactions",
            data={"payload": '{"user":{"id":"%s"}, "callback_id":"vote_team_leader"}' % "test"},
        )

        self.assertEqual(response.status_code, 200)
