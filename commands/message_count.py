from flask import request

from commands.slash_command import SlashCommand


class MessageCountCommand(SlashCommand):
    def __init__(self, bot):
        self.client = bot.client
        self.message_counts = bot.message_counts
        self.icon = bot.ICON
        self.send_message = bot.send_message

    def handler(self):
        data = request.form
        user_name = data.get("user_name", 0)
        user_id = data.get("user_id", 0)
        channel = data.get("channel_id", 0)
        text = f"<@{user_name}> sent {self.message_counts[user_id]} messages."
        self.send_message(text, channel)
