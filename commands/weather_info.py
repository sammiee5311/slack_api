from api.weather import WeatherApi
from flask import request
from slack import WebClient

from commands.slash_command import SlashCommand


class WeatherInfoCommand(SlashCommand):
    def __init__(self, bot):
        self.client: WebClient = bot.client
        self.send_message = bot.send_message
        self.weather_api = WeatherApi()

    def handler(self):
        data = request.form
        channel = f"@{data.get('user_id', '')}"
        city = data.get('text', '').lstrip().rstrip().title()

        if city not in self.weather_api.cities:
            self.send_message('Please write supported city name.', channel)
            return

        current_weather = self.weather_api.get_current_weather(city=city)
        channel = channel
        text = f"Current weather is *{current_weather}*."
        self.send_message(text, channel)
