import requests


def get_storage_dict(nmproduct : str):
    mass = []
    session = requests.Session()
    url = f'https://card.wb.ru/cards/detail?spp=27&regions=64,58,83,4,38,80,33,70,82,86,30,69,22,66,31,40,1,48' \
          f'&pricemarginCoeff=1.0&reg=1&appType=1&emp=0&locale=ru&lang=ru&curr=rub' \
          f'&dest=-1221148,-140294,-1701956,123585768&nm={nmproduct}'
    request = session.get(url)
    json_code = request.json()
    session.close()
    for product in json_code['data']['products']:
        for data in product['sizes']:
            mass.append(data['stocks'])#TODO
    dict_storage_nmproduct = dict('')
    for product in mass:
        for data_storage in product:
            dict_storage_nmproduct[data_storage['wh']] = data_storage['qty']
    return dict_storage_nmproduct


def get_storage_data(mass_nmproduct : [str]):
    main_dict = dict('')
    for nmproduct in mass_nmproduct:
        dicts = get_storage_dict(nmproduct)
        main_dict[nmproduct] = dicts
    return main_dict
