from flask import request

from commands.slash_command import SlashCommand
from database.models import People


class DatabaseCommand(SlashCommand):
    def __init__(self, bot, db_control):
        self.client = bot.client
        self.icon = bot.ICON
        self.send_meesage = bot.send_message
        self.db_control = db_control

    def handler(self):
        data = request.form
        user = data.get("user_id", "")
        text = data.get("text", "").lstrip().rstrip()
        channel = f"@{user}"

        if text == 'init':
            self.db_control.create_database()
        elif text.startswith('insert'):
            info = text.split('-')[1]
            user_data = info.split(',')
            name, team = None, None
            for data in user_data:
                data = data.split('=')
                target = data[0].lstrip().rstrip()
                if target == 'name':
                    name = data[1]
                elif target == 'team':
                    team = data[1]
            
            query = dict(name=name, team=team, user_id=user)
            self.db_control.insert_data(query, People)

        self.send_meesage("Done", channel)

