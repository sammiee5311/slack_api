import os
from collections import defaultdict

import slack
from flask import Flask

from config.config import load_env
from endpoints._flask import (
    FlaskAppWrapper,
    MessageCountCommand,
    VoteCommand,
    WeatherInfoCommand,
)
from endpoints._slack import MessageEvent, ReactionEvent, SlackEventWrapper
from message import WelcomeMessage


class SlackBot:
    def __init__(self):
        self.message_counts = defaultdict(int)
        self.welcome_messages = defaultdict(dict)
        self.client = slack.WebClient(token=os.environ["SLACK_TOKEN"])
        self.BOT_ID = self.client.api_call("auth.test")["user_id"]
        self.vote_table = defaultdict(dict)
        self.welcome = WelcomeMessage()

    def message(self, event):
        channel_id = event.get("channel")
        if "files" in event:
            image_url = event.get("files", "")[0].get("url_private_download")
        user_id = event.get("user", 0)
        text = event.get("text")

        if user_id and self.BOT_ID != user_id:
            self.message_counts[user_id] += 1
            # self.client.chat_postMessage(channel=channel_id, text=text)

            if text.lower() == "start":
                self.welcome.send_message(f"@{user_id}", user_id)

    def reaction(self, event):
        channel_id = event.get("item", {}).get("channel")
        user_id = f"@{event.get('user', 0)}"

        if user_id not in self.welcome.messages:
            return

        welcome = self.welcome.messages[user_id][user_id[1:]]
        welcome.completed = True
        welcome.channel = channel_id
        message = welcome.get_message(channel_id)
        updated_message = self.client.chat_update(**message)
        welcome.timestamp = updated_message["ts"]


if __name__ == "__main__":
    load_env()
    bot = SlackBot()
    flask = FlaskAppWrapper(Flask(__name__))

    vote_command = VoteCommand(bot.client)
    message_count_command = MessageCountCommand(bot.client)
    weather_info_command = WeatherInfoCommand(bot.client)

    slack_wrapper = SlackEventWrapper(flask.app)

    message_event = MessageEvent(bot)
    reaction_event = ReactionEvent(bot)

    flask.add_endpoint(
        endpoint="/message-count",
        endpoint_name="message-count",
        handler=message_count_command.handler,
        methods=["POST"],
    )
    flask.add_endpoint(
        endpoint="/weather", endpoint_name="weather", handler=weather_info_command.handler, methods=["POST"]
    )
    flask.add_endpoint(endpoint="/vote", endpoint_name="vote", handler=vote_command.handler, methods=["POST"])

    slack_wrapper.add_hanlders(event="message", handler=message_event.handler)
    slack_wrapper.add_hanlders(event="reaction_added", handler=reaction_event.handler)

    flask.run()
