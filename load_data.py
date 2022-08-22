import requests
import argparse
import sys
import re

from os import listdir
from os.path import isfile, join
from datetime import datetime, timedelta
from calc import get_frequency_stats

data_path = "data"


def create_parser():
    r = argparse.ArgumentParser()
    r.add_argument('-t', '--text')
    return r


def get_all_product_niche(text: str):
    iterator_page = 1
    temp_mass = []
    mass = []
    avr_mass = []
    while True:
        request = requests.get(
            'https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&curr=rub&emp=0&lang=ru&locale=ru&page=' + str(
                iterator_page) + '&pricemarginCoeff=1.0&query=' + text + '&resultset=catalog&spp=0')
        json_code = request.json()
        temp_mass.append(str(json_code))
        if 'data' not in json_code:
            break
        for product in json_code['data']['products']:
            mass.append((product['name'], product['id']))
        iterator_page += 1
        break
    for data in mass:
        request = requests.get('https://wbx-content-v2.wbstatic.net/price-history/' + str(data[1]) + '.json?')
        if request.status_code != 200:
            continue
        json_code = request.json()
        sum = json_code[len(json_code) - 1]['price']['RUB']
        count = 1
        for obj in json_code:
            time_data = datetime.fromtimestamp(obj['dt'])
            last_month = datetime.now() - timedelta(days=30)
            if time_data > last_month:
                sum += obj['price']['RUB']
                count += 1
        avr_mass.append(sum / count)
    with open(join(data_path, text + ".txt"), 'w+', encoding='utf-8') as f:
        for i in range(len(avr_mass)):
            if i % 10 == 0:
                f.write("\n")
            f.write(str(avr_mass[i]) + ",")


def load_data(filename: str) -> list[float]:
    result = []
    with (open(filename, "r")) as file:
        lines = file.readlines()
        for line in lines:
            for cost in line.split(","):
                if cost != "" and cost != "\n":
                    result.append(float(cost))
    return result


if __name__ == '__main__':
    # parser = create_parser()
    # namespace = parser.parse_args(sys.argv[1:])
    # text_to_search = namespace.text.lower()
    text_to_search = "куртка"
    text_to_search = re.sub(' +', ' ', text_to_search)
    only_files = [f.split('.')[0] for f in listdir(data_path) if isfile(join(data_path, f))]
    if not only_files.__contains__(text_to_search):
        get_all_product_niche(text_to_search)
    filename = str(join(data_path, text_to_search + ".txt"))
    cost_data = load_data(filename)
    n_samples = int(len(cost_data) * 0.1)  # todo think about number of samples
    x, y = get_frequency_stats(cost_data, n_samples)
    with (open("out.txt", "w")) as file:
        for i in range(len(x)):
            file.write(f'{x[i]}, {y[i]}\n')



