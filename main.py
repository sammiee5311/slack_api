from dataclasses import dataclass, field
from typing import List

from flask import Flask

from bot import SlackBot
from commands.classify import ClassifyCommand
from commands.database import DatabaseCommand
from commands.help import HelpCommnad
from commands.kubeflow import KubeflowCommand
from commands.message_count import MessageCountCommand
from commands.slash_command import SlashCommand
from commands.translation import TranslationCommand
from commands.vote import VoteCommand
from commands.weather_info import WeatherInfoCommand
from config import config
from database.control import ControlDatabase
from database.models import db
from endpoints._flask import FlaskAppWrapper, Interactions
from endpoints._slack import MessageEvent, ReactionEvent, SlackEventWrapper


@dataclass
class FlaskEndpointCommand:
    command: SlashCommand
    endpoint: str
    endpoint_name: str
    methods: List = field(default_factory=lambda: ["POST"])


config.load_env()
bot = SlackBot()
flask = FlaskAppWrapper(Flask(__name__))

db.init_app(flask.app)
db_control = ControlDatabase(db)

vote_command = FlaskEndpointCommand(command=VoteCommand(bot), endpoint="/vote", endpoint_name='vote')
message_count_command = FlaskEndpointCommand(command=MessageCountCommand(bot), endpoint="/message-count", endpoint_name="message-count")
weather_info_command = FlaskEndpointCommand(WeatherInfoCommand(bot), endpoint="/weather", endpoint_name="weather")
translation_command = FlaskEndpointCommand(TranslationCommand(bot), endpoint="/translation", endpoint_name="translation")
help_command = FlaskEndpointCommand(HelpCommnad(bot), endpoint="/help", endpoint_name="help")
classify_command = FlaskEndpointCommand(ClassifyCommand(bot, db_control), endpoint="/classify", endpoint_name="classify")
database_command = FlaskEndpointCommand(DatabaseCommand(bot, db_control), endpoint="/db", endpoint_name="database")
kubeflow_command = FlaskEndpointCommand(KubeflowCommand(bot), endpoint="/kubeflow", endpoint_name="kubeflow")

command_endpoints = [vote_command, message_count_command, weather_info_command, translation_command, 
                     help_command, classify_command, database_command, kubeflow_command]

interactions = Interactions(bot)

slack_wrapper = SlackEventWrapper(flask.app)

message_event = MessageEvent(bot)
reaction_event = ReactionEvent(bot)

for command_endpoint in command_endpoints:
    flask.add_endpoint(endpoint=command_endpoint.endpoint,
                       endpoint_name=command_endpoint.endpoint_name,
                       handler=command_endpoint.command.handler,
                       methods=command_endpoint.methods)

slack_wrapper.add_hanlders(event="message", handler=message_event.handler)
slack_wrapper.add_hanlders(event="reaction_added", handler=reaction_event.handler)

flask.run()
