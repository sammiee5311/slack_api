from abc import ABC, abstractmethod
from collections import defaultdict

from api.weather import WeatherApi
from flask import Response, request
from slack import WebClient


class EndpointAction:
    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        self.action()
        return self.response


class FlaskAppWrapper:
    def __init__(self, flask):
        self.app = flask

    def run(self):
        self.app.run()

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler), methods=methods)


class SlashCommand(ABC):
    @abstractmethod
    def __init__(self, client: WebClient):
        """init method"""

    @abstractmethod
    def handler(self):
        """slash command handler"""


class VoteCommand(SlashCommand):
    def __init__(self, client: WebClient):
        self.client = client
        self.vote_table = defaultdict(dict)

    def handler(self):
        data = request.form
        user = data.get("user_id", "")
        target = data.get("text", "")
        channel = data.get("channel_id", 0)

        if not target:
            self.client.chat_postMessage(channel=channel, text=f"Please, choose a user.")
            return

        if user in self.vote_table[channel]:
            self.client.chat_postMessage(
                channel=channel, text=f"Sorry, each person can vote once. (<@{user}> already voted.)"
            )
            return

        self.vote_table[channel][user] = target
        self.client.chat_postMessage(channel=channel, text=f"<@{user}> just voted now.")


class MessageCountCommand(SlashCommand):
    def __init__(self, client: WebClient):
        self.client = client

    def handler(self):
        data = request.form
        user_name = data.get("user_name", 0)
        user_id = data.get("user_id", 0)
        channel_id = data.get("channel_id", 0)
        self.client.chat_postMessage(
            channel=channel_id, text=f"{user_name} sent {self.message_counts[user_id]} messages."
        )


class WeatherInfoCommand(SlashCommand):
    def __init__(self, client: WebClient):
        self.client = client

    def handler(self):
        weather_api = WeatherApi()
        data = request.form
        channel_id = data.get("channel_id", 0)
        current_weather = weather_api.get_current_weather()
        self.client.chat_postMessage(channel=channel_id, text=f"Current weather is {current_weather}.")
