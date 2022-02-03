import sys

import os

import requests
from PIL import Image

toponym_to_find = " ".join(sys.argv[1:])

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    pass
else:
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"].split()
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    address_ll = ','.join(toponym_coodrinates)

    search_params = {
        "apikey": api_key,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": address_ll,
        "type": "biz",
        "results": 10
    }

    response = requests.get(search_api_server, params=search_params)
    if not response:
        pass
    else:
        json_org = response.json()
        organizations = json_org['features']
        with open('test.json', 'w', encoding='utf-8') as f:
            f.write(str(organizations))
        lcs, ucs = [], []
        crugls = []
        comps_coords = []
        for org in organizations:
            comp_coords = comp_long, comp_lat = org['geometry']['coordinates']
            try:
                crugl = org['properties']['CompanyMetaData']['Hours']['Availabilities'][0]['Everyday']
            except KeyError:
                crugl = None
            lc2, uc2 = comp_bound = org['properties']['boundedBy']
            comps_coords.append(comp_coords)
            lcs.append(lc2)
            ucs.append(uc2)
            crugls.append(crugl)
        if len(crugls) == 10:
            toponym_longitude, toponym_lattitude = toponym_coodrinates
            map_params = {
                "l": "map"
            }
            pt = f'{",".join(toponym_coodrinates)},home'
            for i in range(len(crugls)):
                if crugls[i] == True:
                    pt += f'~{",".join(list(map(str, comps_coords[i])))},pm2gnl'
                elif crugls[i] == False:
                    pt += f'~{",".join(list(map(str, comps_coords[i])))},pm2bll'
                else:
                    pt += f'~{",".join(list(map(str, comps_coords[i])))},pm2grl'
            map_params['pt'] = pt
            map_api_server = "http://static-maps.yandex.ru/1.x/"

            response = requests.get(map_api_server, params=map_params)
            with open('image.jpg', mode='wb') as f:
                f.write(response.content)
            Image.open('image.jpg').show()
            os.remove('image.jpg')
        else:
            print("ОШИБКА! По близости не найдено 10 аптек")
            exit(0)
