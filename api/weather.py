import json
import os
from typing import List

import requests


class WeatherApi:
    def __init__(self):
        self.apikey = os.environ["WEATHER_API_KEY"]
        self.cities = self.get_cities()
    
    def get_cities(self) -> List[str]:
        with open('./config/commands/city_list.json', "r") as file:
            json_files = json.load(file)
            cities = []

            for ob in json_files:
                cities.append(ob['name'])

        return cities

    def get_current_weather(self, city: str="Seoul") -> str:
        endpoint = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.apikey}"
        url = endpoint.format(key=self.apikey)
        res = requests.get(url)
        data = json.loads(res.text)
        return data["weather"][0]["main"]
