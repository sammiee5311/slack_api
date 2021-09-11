import os
import sys

from flask.app import Flask

sys.path.append("..")

from unittest import TestCase

from bot import SlackBot
from commands.message_count import MessageCountCommand
from commands.translation import TranslationCommand
from commands.vote import VoteCommand
from commands.weather_info import WeatherInfoCommand
from config.config import load_env
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
        self.flask.add_endpoint(
            endpoint="/weather", endpoint_name="weather", handler=weather_info_command.handler, methods=["POST"]
        )
        response = self.client.post("/weather", data=dict(channel_id="test"))

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
        texts = ["", "hi", "hi --lang ko"]
        self.flask.add_endpoint(
            endpoint="/translation", endpoint_name="translation", handler=translation_command.handler, methods=["POST"]
        )

        for text in texts:
            response = self.client.post("translation", data=dict(user_id=self.test_id, text=text))

            self.assertEqual(response.status_code, 200)
