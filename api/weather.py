import json
import os

import requests


class WeatherApi:
    def __init__(self, city="Seoul"):
        self.apikey = os.environ["WEATHER_API_KEY"]
        self.api = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.apikey}"

    def get_current_weather(self):
        url = self.api.format(key=self.apikey)
        res = requests.get(url)
        data = json.loads(res.text)
        return data["weather"][0]["main"]
