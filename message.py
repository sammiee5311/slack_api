import os
from abc import ABC, abstractmethod
from collections import defaultdict

import slack


class Message(ABC):
    @abstractmethod
    def send_message(self):
        """send message to slack"""


class WelcomeMessage(Message):
    START_TEXT = {
        "type": "section",
        "text": {"type": "mrkdwn", "text": ("Welcome to test channel! \n\n" "*Get started by comepleting the tasks!*")},
    }

    DIVIDER = {"type": "divider"}

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
        check_mark = ":white_check_mark:"
        if not self.completed:
            check_mark = ":white_large_square:"

        text = f"{check_mark} *React to this message!*"

        return {"type": "section", "text": {"type": "mrkdwn", "text": text}}
