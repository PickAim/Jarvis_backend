import re
from urllib import response
import requests


class WildBerriesDataProvider:

    def __init__(self, api_key: str):
        self.__api_key = api_key
        self.__session = requests.Session()

    def get_categories(self) -> list[str]:
        response = self.__session.get('https://suppliers-api.wildberries.ru/api/v1/config/get/object/parent/list',
                                      headers={'Authorization': self.__api_key})
        categories = []
        data = response.json()['data']
        for item in data:
            categories.append(item)
        return categories

    def get_niches(self, categories) -> dict[str, list[str]]:
        result = {}
        for category in categories:
            response = self.__session.get(f'https://suppliers-api.wildberries.ru/api/v1/config/object/byparent?parent={category}',
                                          headers={'Authorization': self.__api_key})
            niches = []
            for niche in response.json()['data']:
                niches.append(niche['name'])
            niches.sort()
            result[category] = niches
        return result
