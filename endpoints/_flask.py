import json
from abc import ABC, abstractmethod
from collections import defaultdict

from api.weather import WeatherApi
from flask import Response, request


class EndpointAction:
    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        self.action()
        return self.response


class FlaskAppWrapper:
    def __init__(self, flask):
        self.app = flask

    def run(self):
        self.app.run()

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler), methods=methods)


class SlashCommand(ABC):
    @abstractmethod
    def __init__(self, bot):
        """init method"""

    @abstractmethod
    def handler(self):
        """slash command handler"""


class VoteCommand(SlashCommand):
    def __init__(self, bot):
        self.client = bot.client
        self.get_leader = bot.get_leader
        self.vote_table = defaultdict(dict)
        self.icon = bot.ICON
        self.is_vote_system_off = bot.get_current_vote_status
        self.number_of_people_voted = 0
        self.members = self.get_members()
        self.send_message = bot.send_message
        self.set_leader = bot.set_leader

    def get_members(self):
        result = self.client.users_list().get("members")
        members = []

        for member in result:
            members.append(member["name"])

        return members

    def select_team_leader(self):
        user_cnt = defaultdict(int)

        for channel in self.vote_table.keys():
            for user in self.vote_table[channel].values():
                user_cnt[user] += 1

        user_cnt = sorted(user_cnt.items(), key=lambda x: (x[0], -x[1]))
        self.set_leader(user_cnt[0][0])
        self.vote_table.clear()

        return self.get_leader()

    def handler(self):
        data = request.form
        user = data.get("user_id", "")
        target = data.get("text", "").lstrip()
        channel = data.get("channel_id", 0)
        leader = self.get_leader()

        if target.startswith("-"):
            if target.startswith("--leader"):
                text = f"Current team leader is <@{leader}>." if leader else "There is not a team leader yet."
                self.send_message(text, channel)
                return
            else:
                text = "Command not exist."
                self.send_message(text, channel)
                return

        if self.is_vote_system_off():
            text = f"Team Leader: <@{leader}>. No vote system on going now."
            self.send_message(text, channel)
            return

        if target not in self.members:
            text = f"Please, choose a exist user."
            self.send_message(text, channel)
            return

        if user in self.vote_table[channel]:
            text = f"Sorry, each person can vote once. (<@{user}> already voted.)"
            self.send_message(text, channel)
            return

        self.vote_table[channel][user] = target
        self.client.chat_postMessage(channel=channel, text=f"<@{user}> just voted now.")
        self.number_of_people_voted += 1

        if self.number_of_people_voted == len(self.members) - 2:
            leader = self.select_team_leader()
            channel_lists = self.client.conversations_list().get("channels", [])
            for channel_list in channel_lists:
                text = f"Team Leader is selected! \n\n" f"*New Team Leader is <@{leader}>!*"
                self.send_message(text, channel_list.get("id"))


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


class WeatherInfoCommand(SlashCommand):
    def __init__(self, bot):
        self.client = bot.client
        self.icon = bot.ICON
        self.send_message = bot.send_message

    def handler(self):
        weather_api = WeatherApi()
        data = request.form
        channel = data.get("channel_id", 0)
        current_weather = weather_api.get_current_weather()
        channel = channel
        text = f"Current weather is {current_weather}."
        self.send_message(text, channel)


class Interactions:
    def __init__(self, bot):
        self.client = bot.client
        self.icon = bot.ICON
        self.admin_ids = bot.admin_ids
        self.send_message = bot.send_message
        self.get_leader = bot.get_leader
        self.current_vote_status = bot.current_vote_status
        self.set_leader = bot.set_leader

    def handler(self):
        data = request.form["payload"]
        data = json.loads(data)
        user_id = data.get("user", "").get("id", "")
        callback = data.get("callback_id", "")
        channel_lists = self.client.conversations_list().get("channels", [])

        if callback == "vote_team_leader" and user_id in self.admin_ids:
            self.set_leader(None)
            self.vote_team_leader(channel_lists)

    def vote_team_leader(self, channel_lists):
        for channel_list in channel_lists:
            channel = channel_list.get("id")
            text = "Start vote for a new team leader !"
            self.send_message(text, channel)
