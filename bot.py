import os
from collections import defaultdict

import slack
from flask import Flask

from commands.classify import ClassifyCommand
from commands.database import DatabaseCommand
from commands.help import HelpCommnad
from commands.message_count import MessageCountCommand
from commands.translation import TranslationCommand
from commands.vote import VoteCommand
from commands.weather_info import WeatherInfoCommand
from config.config import load_env
from database.control import ControlDatabase
from database.models import People, db
from deep.classification import ClassificationImage
from endpoints._flask import FlaskAppWrapper, Interactions
from endpoints._slack import MessageEvent, ReactionEvent, SlackEventWrapper
from message import WelcomeMessage


class SlackBot:
    def __init__(self):
        self.client = slack.WebClient(token=os.environ["SLACK_TOKEN"])
        self.BOT_ID = self.client.api_call("auth.test")["user_id"]
        self.ICON = "https://emoji.slack-edge.com/T02DBK38URZ/squirrel/465f40c0e0.png"
        self.welcome = WelcomeMessage()
        self.classification = ClassificationImage()
        self.admin_ids = [os.environ["TEST_ID"]]
        self.current_vote_status = False  # False: No Leader

    def set_leader(self, leader):
        self.current_vote_status = True if leader else None

        if leader:
            user = People.query.filter_by(user_id=leader).first()
            user.is_leader = True
        else:
            user = People.query.filter_by(is_leader=True).first()
            user.is_leader = False

        db.session.commit()

    def get_current_vote_status(self):
        return self.current_vote_status

    def send_message(self, text, channel_id):
        self.client.chat_postMessage(
            channel=channel_id,
            text=text,
            icon_url=self.ICON,
        )

    def message(self, event):
        user_id = event.get("user", 0)
        text = event.get("text")
        user = People.query.filter_by(user_id=user_id).first()

        if "files" in event and user.ai_activation:
            image_url = event.get("files", "")[0].get("url_private_download")
            result = self.classification.classify_image(image_url)
            self.send_message(f"Result is *{result}*.", f"@{user_id}")

        if user_id and self.BOT_ID != user_id:
            user.message_cnt = user.message_cnt + 1

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

    db.init_app(flask.app)
    db_control = ControlDatabase(db)

    vote_command = VoteCommand(bot)
    message_count_command = MessageCountCommand(bot)
    weather_info_command = WeatherInfoCommand(bot)
    translation_command = TranslationCommand(bot)
    help_command = HelpCommnad(bot)
    classify_command = ClassifyCommand(bot, db_control)
    database_command = DatabaseCommand(bot, db_control)

    interactions = Interactions(bot)

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
    flask.add_endpoint(
        endpoint="/translation", endpoint_name="translation", handler=translation_command.handler, methods=["POST"]
    )
    flask.add_endpoint(endpoint="/vote", endpoint_name="vote", handler=vote_command.handler, methods=["POST"])
    flask.add_endpoint(
        endpoint="/interactions", endpoint_name="interactions", handler=interactions.handler, methods=["POST"]
    )
    flask.add_endpoint(endpoint="/help", endpoint_name="help", handler=help_command.handler, methods=["POST"])
    flask.add_endpoint(
        endpoint="/classify", endpoint_name="classify", handler=classify_command.handler, methods=["POST"]
    )
    flask.add_endpoint(endpoint='/db', endpoint_name='database', handler=database_command.handler, methods=['POST'])

    slack_wrapper.add_hanlders(event="message", handler=message_event.handler)
    slack_wrapper.add_hanlders(event="reaction_added", handler=reaction_event.handler)

    flask.run()
