import requests

from os.path import exists
from os import mkdir
from . import constants
from os.path import abspath
from os import listdir
from os.path import isfile, join
from datetime import datetime, timedelta
import aiohttp
import asyncio


async def get_page_data(session, data):
    avr_mass = []
    url = 'https://wbx-content-v2.wbstatic.net/price-history/'+str(data)+'.json?'
    async with session.get(url=url) as request:
        response_status = request.status
        if response_status != 200:
            pass
        else:
            json_code = await request.json()
            sum = 0
            count = 1
            for obj in json_code:
                time_data = datetime.fromtimestamp(obj['dt'])
                last_month = datetime.now() - timedelta(days=30)
                if time_data > last_month:
                    sum += obj['price']['RUB']
                    count += 1
            if sum != 0:
                avr_mass.append(sum / count)
            else:
                avr_mass.append(json_code[len(json_code) - 1]['price']['RUB'])
        return avr_mass


async def get_all_product_niche(text: str, output_dir: str, pages_num: int):
    iterator_page = 1
    temp_mass = []
    mass = []
    session = requests.Session()
    while True:
        uri = f'https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=2,12,7,3,6,21,16' \
              f'&curr=rub&dest=-1221148,-140294,-1751445,-364763&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0' \
              f'&query={text}&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false&page={str(iterator_page)}'
        request = session.get(
            uri
        )
        json_code = request.json()
        temp_mass.append(str(json_code))
        if 'data' not in json_code:
            break
        for product in json_code['data']['products']:
            mass.append((product['name'], product['id']))
        iterator_page += 1
        if pages_num != -1 and iterator_page > pages_num:
            break
    session.close()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for data in mass:
            task = asyncio.create_task(get_page_data(session, data[1]))
            tasks.append(task)
        avr_collection = await asyncio.gather(*tasks)
        j = 0
        with open(join(output_dir, text + ".txt"), 'w', encoding='utf-8') as f:
            for avr_mass in avr_collection:
                for i in range(len(avr_mass)):
                    if j % 10 == 0 and j != 0:
                        f.write("\n")
                    j += 1
                    f.write(str(avr_mass[i]) + ",")
    await session.close()


def load(text: str, update: bool = False, pages_num: int = -1):
    only_files = []
    if exists(constants.data_path):
        only_files = [f.split('.')[0] for f in listdir(
            constants.data_path) if isfile(join(constants.data_path, f))]
    else:
        mkdir(constants.data_path)
    if not (text in only_files) or update:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(get_all_product_niche(text, abspath(constants.data_path), pages_num))

