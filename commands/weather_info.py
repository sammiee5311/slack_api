from api.weather import WeatherApi
from flask import request

from commands.slash_command import SlashCommand


class WeatherInfoCommand(SlashCommand):
    def __init__(self, bot):
        self.client = bot.client
        self.send_message = bot.send_message
        self.weather_api = WeatherApi()

    def handler(self):
        data = request.form
        channel = f"@{data.get('user_id', '')}"
        current_weather = self.weather_api.get_current_weather()
        channel = channel
        text = f"Current weather is *{current_weather}*."
        self.send_message(text, channel)
