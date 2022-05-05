# 2. Зарегистрироваться на https://openweathermap.org/api и написать функцию, которая получает погоду в данный момент
# для города, название которого получается через input. https://openweathermap.org/current

import json
import requests
import os
from dotenv import load_dotenv

WEATHER_PATH = "weather.json"
load_dotenv('./.env')
# KELVIN = 273


class CurrentWeather:
    def __init__(self, city):
        self.url = 'https://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s'
        self.city = city
        # self.params = {
        #     'units': 'metric',
        #     'lang': 'ru'
        # }

    @staticmethod
    def get_api_key():
        return os.getenv('APPID')

    def get_url(self, api_key):
        return self.url % (self.city, api_key)

    @staticmethod
    def get_info_weather(url):
        try:
            weather_info = requests.get(url, params={'units': 'metric', 'lang': 'ru'})
            weather_info.raise_for_status()
            weather_info_json = weather_info.json()
            return weather_info_json
        except Exception as e:
            print(e)
        return None

    @staticmethod
    def save_weather(weather_info, path):
        with open(path, "w") as f:
            json.dump(weather_info, f, indent=2)
        print(f'Данные о текущей погоде сохранены в файле {path}.')

    def pipeline(self, path):
        try:
            api_key = self.get_api_key()
            url = self.get_url(api_key)
            data = self.get_info_weather(url)
            print(f'Текущая погода в городе {self.city} - {data["main"]["temp"]} oC.')
            self.save_weather(data, path)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    city_input = input("Введите название города: ")
    weather = CurrentWeather(city_input)
    weather.pipeline(WEATHER_PATH)
