from flask import request

from commands.slash_command import SlashCommand


class ClassifyCommand(SlashCommand):
    def __init__(self, bot):
        self.client = bot.client
        self.send_message = bot.send_message
        self.classify_ids = bot.classify_ids

    def handler(self):
        data = request.form
        user = data.get("user_id", "")
        target = data.get("text", "").lstrip().rstrip()
        channel = f"@{user}"

        if target == "--on":
            self.classify_ids[user] = True
            self.send_message("Classify mode *on*", channel)
        elif target == "--off":
            self.classify_ids[user] = False
            self.send_message("Classify mode *off*", channel)
        else:
            text = "Please type valid text."
            self.send_message(text, channel)
