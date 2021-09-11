import os
import sys

from flask.app import Flask

sys.path.append("..")

from unittest import TestCase

from bot import SlackBot
from config.config import load_env
from endpoints._flask import FlaskAppWrapper


class TestWelcomeMessage(TestCase):
    def setUp(self):
        load_env()
        self.bot = SlackBot()
        self.flask = FlaskAppWrapper(Flask(__name__))
        self.flask.app.config["TESTING"] = True
        self.client = self.flask.app.test_client()
        self.test_id = os.environ["TEST_ID"]

    def test_welcome_message(self):
        self.bot.welcome.send_message(f"@{self.test_id}", self.test_id)
