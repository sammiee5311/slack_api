from bot import SlackBot
from flask import request

from commands.slash_command import SlashCommand
from database.models import People


class MessageCountCommand(SlashCommand):
    def __init__(self, bot: SlackBot):
        self.client = bot.client
        self.icon = bot.ICON
        self.send_message = bot.send_message

    def handler(self):
        data = request.form
        user_name = data.get("user_name", 0)
        user_id = data.get("user_id", 0)
        channel = data.get("channel_id", 0)
        user = People.query.filter_by(user_id=user_id).first()
        text = f"<@{user_name}> sent {user.message_cnt} messages."
        self.send_message(text, channel)
