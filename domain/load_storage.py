import requests

def get_storage_dict(nmproduct : str):
    session = requests.Session()
    url = f'https://card.wb.ru/cards/detail?spp=27&regions=64,58,83,4,38,80,33,70,82,86,30,69,22,66,31,40,1,48' \
          f'&pricemarginCoeff=1.0&reg=1&appType=1&emp=0&locale=ru&lang=ru&curr=rub' \
          f'&dest=-1221148,-140294,-1701956,123585768&nm={nmproduct}'
    request = session.get(url)
    json_code = request.json()
    mass = []
    session.close()
    for product in json_code['data']['products']:
        for i in product['sizes']:
            mass.append(i['stocks'])#TODO
    d = dict('')
    for product in mass:
        for i in product:
            d[i['wh']]=i['qty']
    return d


def get_storage_data(data : [str]):
    main_dict = dict('')
    for i in data:
        dicts = get_storage_dict(i)
        main_dict[i]=dicts
    return main_dict
