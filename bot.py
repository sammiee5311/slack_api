import os

import slack

from database.models import People, db
from deep.classification import ClassificationImage
from message import WelcomeMessage


class SlackBot:
    def __init__(self):
        self.client = slack.WebClient(token=os.environ["SLACK_TOKEN"])
        self.BOT_ID = self.client.api_call("auth.test")["user_id"]
        self.ICON = "https://emoji.slack-edge.com/T02DBK38URZ/squirrel/465f40c0e0.png"
        self.welcome = WelcomeMessage()
        self.classification = ClassificationImage()
        self.admin_ids = [os.environ["TEST_ID"]]
        self.current_vote_status = False  # False: No Leader

    def set_leader(self, leader):
        self.current_vote_status = True if leader else None

        if leader:
            user = People.query.filter_by(user_id=leader).first()
            user.is_leader = True
        else:
            user = People.query.filter_by(is_leader=True).first()
            user.is_leader = False

        db.session.commit()

    def get_current_vote_status(self):
        return self.current_vote_status

    def send_message(self, text, channel_id):
        self.client.chat_postMessage(
            channel=channel_id,
            text=text,
            icon_url=self.ICON,
        )

    def message(self, event):
        user_id = event.get("user", 0)
        text = event.get("text")
        user = People.query.filter_by(user_id=user_id).first()

        if "files" in event and user.ai_activation:
            image_url = event.get("files", "")[0].get("url_private_download")
            print(image_url)
            try:
                result = self.classification.classify_image(image_url)
                self.send_message(f"Result is *{result}*.", f"@{user_id}")
            except:
                self.send_message(f"The image you sent does not fit for classification.", f"@{user_id}")

        if user_id and self.BOT_ID != user_id:
            user.message_cnt = user.message_cnt + 1
            # db.session.commit()  ## Need to commit every hou

            if text.lower() == "start":
                self.welcome.send_message(f"@{user_id}", user_id)

    def reaction(self, event):
        channel_id = event.get("item", {}).get("channel")
        user_id = f"@{event.get('user', 0)}"

        if user_id not in self.welcome.messages:
            return

        welcome = self.welcome.messages[user_id][user_id[1:]]
        welcome.completed = True
        welcome.channel = channel_id
        message = welcome.get_message(channel_id)
        updated_message = self.client.chat_update(**message)
        welcome.timestamp = updated_message["ts"]

