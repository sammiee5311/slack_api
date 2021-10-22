from bot import SlackBot
from config.commands.help_text import HELP_TEXT
from flask import request
from slack import WebClient

from commands.slash_command import SlashCommand


class HelpCommnad(SlashCommand):
    def __init__(self, bot: SlackBot):
        self.client: WebClient = bot.client
        self.send_message = bot.send_message
        self.commands: str = HELP_TEXT

    def handler(self):
        data = request.form
        user = data.get("user_id", "")
        target = data.get("text", "").lstrip().rstrip()
        channel = f"@{user}"
        text = "Please type valid text."

        if not target:
            commands = "*, *".join(list(self.commands.keys()))
            self.send_message(f"Please type help command with *{commands}*.", channel)
            return

        if target not in self.commands:
            self.send_message(text, channel)
            return

        self.send_message(HELP_TEXT[target], channel)
