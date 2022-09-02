import asyncio
import aiohttp
import json
from datetime import datetime
from types import TracebackType
from typing import Optional, Type


class AsyncWildberriesDataProvider:

    def __init__(self, api_key: str) -> None:
        self.__api_key = api_key

    async def __aenter__(self):
        self.__session = aiohttp.ClientSession()
        return self

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType],):
        await self.__session.close()
        self.__session = None

    async def get_categories(self) -> list[str]:
        async with self.__session.get(
            'https://suppliers-api.wildberries.ru/api/v1/config/get/object/parent/list',
                headers={'Authorization': self.__api_key}) as response:
            response.raise_for_status()
            categories = []
            data = await response.json()
            for item in data['data']:
                categories.append(item)
            return categories

    async def get_niches(self, categories: list[str]) -> dict[str, dict[str, list[str]]]:
        tasks = []
        for category in categories:
            tasks.append(asyncio.create_task(
                self.get_niches_by_category(category)))
        niche_sets = await asyncio.gather(*tasks)
        return dict(zip(categories, niche_sets))

    async def get_niches_by_category(self, category: str):
        url = f'https://suppliers-api.wildberries.ru/api/v1/config/object/byparent?parent={category}'
        async with self.__session.get(url, headers={'Authorization': self.__api_key}) as response:
            response.raise_for_status()
            niches = []
            data = await response.json()
            for niche in data['data']:
                niches.append(niche['name'])
            niches.sort()
            return niches

    async def get_products_by_niche(self, niche: str, pages: int) -> list[tuple[str, int]]:
        tasks = []
        for i in range(1, pages + 1):
            tasks.append(asyncio.create_task(
                self.__search_products_by_page(niche, i)))
        result = []
        product_sets = await asyncio.gather(*tasks)
        for set in product_sets:
            result.extend(set)
        return result

    async def __search_products_by_page(self, niche: str, page: int) -> list[tuple[str, int]]:
        uri = 'https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=2,12,7,3,6,21,16' \
            '&curr=rub&dest=-1221148,-140294,-1751445,-364763&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0' \
            f'&query={niche}&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false&page={page}'
        result = []
        async with self.__session.get(uri) as response:
            response.raise_for_status()
            data = await response.read()
            json_data = json.loads(data)
            if 'data' not in json_data:
                return result
            for product in json_data['data']['products']:
                result.append((product['name'], product['id']))
            return result

    async def get_product_price_history(self, product_id: int) -> list[tuple[int, datetime]]:
        uri = f'https://wbx-content-v2.wbstatic.net/price-history/{product_id}.json?'
        result = []
        async with self.__session.get(uri) as response:
            response.raise_for_status()
            if response.status != 200:
                return result
            data = await response.json()
            for item in data:
                result.append(
                    (item['price']['RUB'], datetime.fromtimestamp(item['dt'])))
            return result
