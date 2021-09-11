from collections import defaultdict

from flask import request

from commands.slash_command import SlashCommand


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

        return members + ["test"]

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

        if self.number_of_people_voted == len(self.members) - 2 or target == "test":
            leader = self.select_team_leader()
            if target == "test":
                return
            channel_lists = self.client.conversations_list().get("channels", [])
            for channel_list in channel_lists:
                text = f"Team Leader is selected! \n\n" f"*New Team Leader is <@{leader}>!*"
                self.send_message(text, channel_list.get("id"))
