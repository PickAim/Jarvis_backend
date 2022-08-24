import requests
import json


def get_parent():
    request = requests.get('https://suppliers-api.wildberries.ru/api/v1/config/get/object/parent/list',
                           headers={
                               'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
                                                '.eyJhY2Nlc3NJRCI6IjZkNDVmMmRjLTQ5ODEtNDFlOS1hMzRkLTlhNDA5YmY2MGZiMSJ9.1VoUp9Od9dzSWSNVSQjQnRujUvqOUY4oxO-pZXAqI1Q'})
    json_code = request.json()
    category = []
    for i in json_code['data']:
        category.append(i)
    return category


def get_niche():
    category = get_parent()
    dict_niche_by_category = dict()
    for i in category:
        request = requests.get('https://suppliers-api.wildberries.ru/api/v1/config/object/byparent?parent=' + i,
                               headers={
                                   'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
                                                    '.eyJhY2Nlc3NJRCI6IjZkNDVmMmRjLTQ5ODEtNDFlOS1hMzRkLTlhNDA5YmY2MGZiMSJ9.1VoUp9Od9dzSWSNVSQjQnRujUvqOUY4oxO-pZXAqI1Q'})
        json_code = request.json()
        niche = []
        for j in json_code['data']:
            niche.append(j['name'])
        dict_niche_by_category[i] = niche
    with open("data_file.json", "w", encoding='utf-8') as write_file:
        for chunk in json.JSONEncoder(ensure_ascii=False).iterencode(dict_niche_by_category):
            write_file.write(chunk)


if __name__ == '__main__':
    get_niche()
