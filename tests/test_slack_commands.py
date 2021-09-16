import os
import sys

from flask.app import Flask

sys.path.append("..")

from unittest import TestCase

from bot import SlackBot
from commands.classify import ClassifyCommand
from commands.help import HelpCommnad
from commands.message_count import MessageCountCommand
from commands.translation import TranslationCommand
from commands.vote import VoteCommand
from commands.weather_info import WeatherInfoCommand
from config.commands.help_text import HELP_TEXT
from config.config import load_env
from deep.classification import ClassificationImage
from endpoints._flask import FlaskAppWrapper


class TestCommand(TestCase):
    def setUp(self):
        load_env()
        self.bot = SlackBot()
        self.flask = FlaskAppWrapper(Flask(__name__))
        self.flask.app.config["TESTING"] = True
        self.client = self.flask.app.test_client()
        self.test_id = os.environ["TEST_ID"]

    def test_weather_command(self):
        weather_info_command = WeatherInfoCommand(self.bot)
        texts = ["test", "Seoul", "New York"]
        self.flask.add_endpoint(
            endpoint="/weather", endpoint_name="weather", handler=weather_info_command.handler, methods=["POST"]
        )
        for text in texts:
            response = self.client.post("/weather", data=dict(user_id=self.test_id, channel_id="test", text=text))

            self.assertEqual(response.status_code, 200)

    def test_vote_command(self):
        vote_command = VoteCommand(self.bot)
        self.flask.add_endpoint(endpoint="/vote", endpoint_name="vote", handler=vote_command.handler, methods=["POST"])

        texts = ["", "testest123", "test", "--leader", "--test", "test"]
        for text in texts:
            response = self.client.post("vote", data=dict(user_id=self.test_id, text=text, channel_id="test"))

            self.assertEqual(response.status_code, 200)

    def test_message_count_command(self):
        message_count_command = MessageCountCommand(self.bot)
        self.flask.add_endpoint(
            endpoint="/message-count",
            endpoint_name="message-count",
            handler=message_count_command.handler,
            methods=["POST"],
        )
        response = self.client.post(
            "message-count", data=dict(user_id=self.test_id, user_name="test", channel_id="test")
        )

        self.assertEqual(response.status_code, 200)

    def test_translation_command(self):
        translation_command = TranslationCommand(self.bot)
        texts = ["", "hi", "hi --lang ko", "hi --lang scc", "--language"]
        self.flask.add_endpoint(
            endpoint="/translation", endpoint_name="translation", handler=translation_command.handler, methods=["POST"]
        )

        for text in texts:
            response = self.client.post("translation", data=dict(user_id=self.test_id, text=text))

            self.assertEqual(response.status_code, 200)

    def test_help_command(self):
        help_command = HelpCommnad(self.bot)
        texts = ["", "test"] + list(HELP_TEXT.keys())
        self.flask.add_endpoint(endpoint="/help", endpoint_name="help", handler=help_command.handler, methods=["POST"])

        for text in texts:
            response = self.client.post("help", data=dict(user_id=self.test_id, text=text))

            self.assertEqual(response.status_code, 200)

    def test_classify_command(self):
        classify_command = ClassifyCommand(self.bot)
        classification = ClassificationImage()
        texts = ["", "--off", '--on']
        self.flask.add_endpoint(
            endpoint='/classify', endpoint_name='classify', handler=classify_command.handler, methods=["POST"]
        )

        for text in texts:
            response = self.client.post('classify', data=dict(user_id=self.test_id, text=text))

            self.assertEqual(response.status_code, 200)
        
        classification.classify_image('https://images.unsplash.com/photo-1537151625747-768eb6cf92b2?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=932&q=80')
