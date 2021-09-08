import os
from abc import ABC, abstractmethod

from slackeventsapi import SlackEventAdapter


class SlackEventWrapper:
    def __init__(self, flask_app):
        self.slack_event_adapter = SlackEventAdapter(os.environ["SIGNING_SECRET"], "/slack/events", flask_app)

    def add_hanlders(self, event, handler):
        self.slack_event_adapter._add_event_handler(event, handler, handler)


class SlackEventHandler(ABC):
    @abstractmethod
    def __init__(self, bot):
        """init method"""

    @abstractmethod
    def handler(self, paylode):
        """slack event handler"""


class MessageEvent(SlackEventHandler):
    def __init__(self, bot):
        self.bot = bot

    def handler(self, payload):
        event = payload.get("event", {})
        self.bot.message(event)


class ReactionEvent(SlackEventHandler):
    def __init__(self, bot):
        self.bot = bot

    def handler(self, payload):
        event = payload.get("event", {})
        self.bot.reaction(event)
