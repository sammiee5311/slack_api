import os
import sys

from flask.app import Flask

sys.path.append("..")

from unittest import TestCase

from bot import SlackBot
from config.config import load_env
from endpoints._flask import FlaskAppWrapper, Interactions


class TestInteractions(TestCase):
    def setUp(self):
        load_env()
        self.bot = SlackBot()
        self.flask = FlaskAppWrapper(Flask(__name__))
        self.flask.app.config["TESTING"] = True
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
