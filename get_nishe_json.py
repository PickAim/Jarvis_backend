import requests
import json
from datetime import datetime, timedelta

def getParent():
    request = requests.get('https://suppliers-api.wildberries.ru/api/v1/config/get/object/parent/list', headers={'Authorization':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjZkNDVmMmRjLTQ5ODEtNDFlOS1hMzRkLTlhNDA5YmY2MGZiMSJ9.1VoUp9Od9dzSWSNVSQjQnRujUvqOUY4oxO-pZXAqI1Q'})
    jsonCode = request.json()
    mass=[]
    for i in jsonCode['data']:
        mass.append(i)
    return mass

def getNishe():
    mass = getParent()
    dictNisheByCategory = dict()
    for i in mass:
        request = requests.get('https://suppliers-api.wildberries.ru/api/v1/config/object/byparent?parent=' + i, headers={'Authorization':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjZkNDVmMmRjLTQ5ODEtNDFlOS1hMzRkLTlhNDA5YmY2MGZiMSJ9.1VoUp9Od9dzSWSNVSQjQnRujUvqOUY4oxO-pZXAqI1Q'})
        jsonCode = request.json()
        mass = []
        for j in jsonCode['data']:
            mass.append(j['name'])
        dictNisheByCategory[i] = mass
        print(dictNisheByCategory)
    with open("data_file.json", "w",encoding='utf-8') as write_file:
        for chunk in json.JSONEncoder(ensure_ascii=False).iterencode(dictNisheByCategory):
            write_file.write(chunk)
    # with open("data_file.json", 'r', encoding='utf-8') as fh:
    #     data = json.load(fh)  # загружаем из файла данные в словарь data

if __name__ == '__main__':
    getNishe()

