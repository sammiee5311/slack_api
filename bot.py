import slack
import os
from pathlib import Path
from PIL import Image
from collections import defaultdict
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from urllib import request
from io import BytesIO
import requests
from skimage import io


ENV_PATH = Path('.') / '.env'
load_dotenv(dotenv_path=ENV_PATH)

app = Flask(__name__)

slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call('auth.test')['user_id']

message_counts = defaultdict(int)
welcome_messages = defaultdict(dict)

class WelcomeMessage:
    START_TEXT = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': (
                'Welcome to test channel! \n\n'
                '*Get started by comepleting the tasks!*'
            )
        }
    }

    DIVIDER = {'type': 'divider'}

    def __init__(self, channel, user):
        self.channel = channel
        self.user = user
        self.icon_emoji = ':robot_face:'
        self.timestamp = ''
        self.completed = False

    def get_message(self):
        return {
            'ts': self.timestamp,
            'channel': self.channel,
            'username': 'Welcome Bot!',
            'icon_emoji': self.icon_emoji,
            'blocks': [
                self.START_TEXT,
                self.DIVIDER,
                self._get_reaction_task()
            ]
        }

    def _get_reaction_task(self):
        check_mark = ':white_check_mark:'
        if not self.completed:
            check_mark =':white_large_square:'
        
        text = f"{check_mark} *React to this message!*"

        return {'type': 'section', 'text': {'type': 'mrkdwn', 'text': text}}


def send_welcome_message(channel, user):
    welcome = WelcomeMessage(channel, user)
    message = welcome.get_message()
    response = client.chat_postMessage(**message)
    welcome.timestamp = response['ts']

    welcome_messages[channel][user] = welcome


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    image_url = event.get('files', '')[0].get('url_private_download')
    user_id = event.get('user', 0)
    text = event.get('text')

    if user_id and BOT_ID != user_id:
        message_counts[user_id] += 1
        # client.chat_postMessage(channel=channel_id, text=text)

        if text.lower() == 'start':
            send_welcome_message(f"@{user_id}", user_id)


@slack_event_adapter.on('reaction_added')
def reaction(payload):
    event = payload.get('event', {})
    channel_id = event.get('item', {}).get('channel')
    user_id = f"@{event.get('user', 0)}"

    if user_id not in welcome_messages:
        return

    welcome = welcome_messages[user_id][user_id[1:]]
    welcome.completed = True
    welcome.channel = channel_id
    message = welcome.get_message()
    updated_message = client.chat_update(**message)
    welcome.timestamp = updated_message['ts']


@app.route('/message-count', methods=['POST'])
def message_count():
    data = request.form
    user_name = data.get('user_name', 0)
    user_id = data.get('user_id', 0)
    channel_id = data.get('channel_id', 0)
    client.chat_postMessage(channel=channel_id, text=f"{user_name} sends {message_counts[user_id]} messages.")
    return Response(), 200


if __name__ == '__main__':
    app.run(debug=True)
