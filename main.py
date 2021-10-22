from flask import Flask

from bot import SlackBot
from commands.classify import ClassifyCommand
from commands.database import DatabaseCommand
from commands.help import HelpCommnad
from commands.kubeflow import KubeflowCommand
from commands.message_count import MessageCountCommand
from commands.translation import TranslationCommand
from commands.vote import VoteCommand
from commands.weather_info import WeatherInfoCommand
from config import config
from database.control import ControlDatabase
from database.models import db
from endpoints._flask import FlaskAppWrapper, Interactions
from endpoints._slack import MessageEvent, ReactionEvent, SlackEventWrapper

config.load_env()
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
kubeflow_command = KubeflowCommand(bot)

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
flask.add_endpoint(endpoint='/kubeflow', endpoint_name='kubeflow', handler=kubeflow_command.handler, methods=["POST"])

slack_wrapper.add_hanlders(event="message", handler=message_event.handler)
slack_wrapper.add_hanlders(event="reaction_added", handler=reaction_event.handler)

flask.run()
