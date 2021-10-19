import os
import sys

from flask.app import Flask

sys.path.append("..")

from unittest import TestCase

from bot import SlackBot
from config import config

from tests.test_flask import FlaskAppWrapper


class TestWelcomeMessage(TestCase):
    def setUp(self):
        config.load_env()
        self.bot = SlackBot()
        self.flask = FlaskAppWrapper(Flask(__name__))
        self.client = self.flask.app.test_client()
        self.test_id = os.environ["TEST_ID"]

    def test_welcome_message(self):
        self.bot.welcome.send_message(f"@{self.test_id}", self.test_id)
