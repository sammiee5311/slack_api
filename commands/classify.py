from bot import SlackBot
from flask import request

from commands.slash_command import SlashCommand
from database.models import People


class ClassifyCommand(SlashCommand):
    def __init__(self, bot: SlackBot, db):
        self.client = bot.client
        self.send_message = bot.send_message
        self.database = db
    
    def set_turn_on_or_off(self, state, user):
        user = People.query.filter_by(user_id=user).first()
        user.ai_activation = state
        self.database.db.session.commit()

    def handler(self):
        data = request.form
        user = data.get("user_id", "")
        target = data.get("text", "").lstrip().rstrip()
        channel = f"@{user}"

        if target == "--on":
            self.set_turn_on_or_off(True, user)
            self.send_message("Classify mode *on*", channel)
        elif target == "--off":
            self.set_turn_on_or_off(False, user)
            self.send_message("Classify mode *off*", channel)
        else:
            text = "Please type valid text."
            self.send_message(text, channel)
