import json

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
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///slack-api.db"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    def run(self):
        self.app.run()

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler), methods=methods)


class Interactions:
    def __init__(self, bot):
        self.client = bot.client
        self.icon = bot.ICON
        self.admin_ids = bot.admin_ids
        self.send_message = bot.send_message
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
