import requests
import json


def get_parent():
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=100,
        pool_maxsize=100)
    session.mount('http://', adapter)
    response = session.get('https://suppliers-api.wildberries.ru/api/v1/config/get/object/parent/list',
                           headers={
                               'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
                                                '.eyJhY2Nlc3NJRCI6IjZkNDVmMmRjLTQ5ODEtNDFlOS1hMzRkLTlhNDA5YmY2MGZiMSJ9.1VoUp9Od9dzSWSNVSQjQnRujUvqOUY4oxO-pZXAqI1Q'})
    json_code = response.json()
    category = []
    for data in json_code['data']:
        category.append(data)
    return category


def get_niche():
    categories = get_parent()
    dict_niche_by_category = dict()
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=100,
        pool_maxsize=100)
    session.mount('http://', adapter)
    for category in categories:
        response = session.get('https://suppliers-api.wildberries.ru/api/v1/config/object/byparent?parent=' + category,
                               headers={
                                   'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
                                                    '.eyJhY2Nlc3NJRCI6IjZkNDVmMmRjLTQ5ODEtNDFlOS1hMzRkLTlhNDA5YmY2MGZiMSJ9.1VoUp9Od9dzSWSNVSQjQnRujUvqOUY4oxO-pZXAqI1Q'})
        json_code = response.json()
        niche = []
        for data in json_code['data']:
            niche.append(data['name'])
        niche.sort()
        dict_niche_by_category[category] = niche
    with open("data_file.json", "w", encoding='utf-8') as write_file:
        json.dump(dict_niche_by_category, write_file, ensure_ascii=False)


if __name__ == '__main__':
    get_niche()
