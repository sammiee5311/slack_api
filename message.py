import os
from abc import ABC, abstractmethod
from collections import defaultdict

import slack


class Message(ABC):
    DIVIDER = {"type": "divider"}
    @abstractmethod
    def send_message(self):
        """send message to slack"""


class WelcomeMessage(Message):
    START_TEXT = {
        "type": "section",
        "text": {"type": "mrkdwn", "text": ("Welcome to test channel! \n\n" "*Get started by comepleting the tasks!*")},
    }

    def __init__(self):
        self.icon_emoji = ":robot_face:"
        self.timestamp = ""
        self.completed = False
        self.messages = defaultdict(dict)
        self.client = slack.WebClient(token=os.environ["SLACK_TOKEN"])

    def send_message(self, channel, user):
        message = self.get_message(channel)
        response = self.client.chat_postMessage(**message)
        self.timestamp = response["ts"]

        self.messages[channel][user] = self

    def get_message(self, channel):
        return {
            "ts": self.timestamp,
            "channel": channel,
            "username": "Welcome Bot!",
            "icon_emoji": self.icon_emoji,
            "blocks": [self.START_TEXT, self.DIVIDER, self._get_reaction_task()],
        }

    def _get_reaction_task(self):
        doc_link = os.environ["DOC_LINK"]

        text = (
            f"*Please, read our <{doc_link}|DOC>!* \n\n"
            f"*We have weather and translation api currently!* \n\n"
            f"*To see instructions of our provided api, simply type /help!*"
        )

        return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


class KubeflowMessage(Message):
    def __init__(self, client):
        self.client = client

    def send_message(self, channel, text, info, link):
        self.info = info
        self.link = link
        self.text = text
        self.START_TEXT = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": text},
            }
        message = self.get_message(channel)
        self.client.chat_postMessage(**message)

    def get_message(self, channel):
        return {
            "channel": channel,
            "username": "Kubeflow Alert",
            "blocks": [self.START_TEXT, self.DIVIDER, self.get_info(), self.DIVIDER, self.get_button()],
        }

    def get_info(self):
        text = self.info

        return {"type": "section", "text": {"type": "mrkdwn", "text": text}}

    def get_button(self):
        return {"type": "actions", "elements": [{"type": "button", "text": { "type": "plain_text", "text": f"check {self.text.split(' ')[-1][:-1]}"}, "value": "click", "url": self.link }] }
