import requests
import sys
import re
import constants

from os import listdir
from os.path import isfile, join
from datetime import datetime, timedelta
from calc import get_frequency_stats
from jarvis_utils import create_parser, load_data


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
        break  # todo uncomment after TECHNOPROM
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
    with open(join(constants.data_path, text + ".txt"), 'w+', encoding='utf-8') as f:
        for i in range(len(avr_mass)):
            if i % 10 == 0:
                f.write("\n")
            f.write(str(avr_mass[i]) + ",")


if __name__ == '__main__':
    parser = create_parser([('-t', '--text')])
    namespace = parser.parse_args(sys.argv[1:])
    text_to_search = namespace.text.lower()
    text_to_search = re.sub(' +', ' ', text_to_search)
    only_files = [f.split('.')[0] for f in listdir(constants.data_path) if isfile(join(constants.data_path, f))]
    if not only_files.__contains__(text_to_search):
        get_all_product_niche(text_to_search)
    filename = str(join(constants.data_path, text_to_search + ".txt"))
    cost_data = load_data(filename)
    n_samples = int(len(cost_data) * 0.1)  # todo think about number of samples
    x, y = get_frequency_stats(cost_data, n_samples)
    with (open(join(constants.out_path, "out.txt"), "w")) as file:
        for i in range(len(x)):
            file.write(f'{x[i]}, {y[i]}\n')
