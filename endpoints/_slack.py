import os
from typing import Protocol, Union

from bot import SlackBot
from flask.app import Flask
from slackeventsapi import SlackEventAdapter


class SlackEventWrapper:
    def __init__(self, flask_app: Flask):
        self.slack_event_adapter = SlackEventAdapter(os.environ["SIGNING_SECRET"], "/slack/events", flask_app)

    def add_hanlders(self, event, handler):
        self.slack_event_adapter._add_event_handler(event, handler, handler)


class SlackEventHandler(Protocol):
    def __init__(self, bot: SlackBot):
        ...

    def handler(self, payload: dict[str, Union[str, list[str]]]):
        ...


class MessageEvent:
    def __init__(self, bot: SlackBot):
        self.bot = bot

    def handler(self, payload: dict[str, Union[str, list[str]]]):
        event = payload.get("event", {})
        self.bot.message(event)


class ReactionEvent:
    def __init__(self, bot: SlackBot):
        self.bot = bot

    def handler(self, payload: dict[str, Union[str, list[str]]]):
        event = payload.get("event", {})
        self.bot.reaction(event)
