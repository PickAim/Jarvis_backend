from datetime import datetime
import requests


class WildBerriesDataProvider:

    def __init__(self, api_key: str):
        self.__api_key = api_key
        self.__session = requests.Session()

    def get_categories(self) -> list[str]:
        response = self.__session.get('https://suppliers-api.wildberries.ru/api/v1/config/get/object/parent/list',
                                      headers={'Authorization': self.__api_key})
        response.raise_for_status()
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
            response.raise_for_status()
            niches = []
            for niche in response.json()['data']:
                niches.append(niche['name'])
            niches.sort()
            result[category] = niches
        return result

    def get_products_by_niche(self, niche: str, pages: int) -> list[tuple[str, int]]:
        result = []
        for i in range(1, pages + 1):
            uri = 'https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=2,12,7,3,6,21,16' \
                '&curr=rub&dest=-1221148,-140294,-1751445,-364763&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0' \
                f'&query={niche}&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false&page={i}'
            response = self.__session.get(uri)
            response.raise_for_status()
            json_data = response.json()
            if 'data' not in json_data:
                break
            for product in json_data['data']['products']:
                result.append((product['name'], product['id']))
        return result

    def get_product_price_history(self, id: int) -> list[tuple[int, datetime]]:
        result = []
        uri = f'https://wbx-content-v2.wbstatic.net/price-history/{id}.json?'
        response = self.__session.get(uri)
        response.raise_for_status()
        if response.status_code != 200:
            return result
        for item in response.json():
            result.append(
                (item['price']['RUB'], datetime.fromtimestamp(item['dt'])))
        return result
