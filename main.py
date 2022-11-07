from pathlib import Path
import requests
import json
import os
import pandas as pd

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}


def get_main_link(item_json):
    ident_code = str(item_json['id'])
    vol = ident_code[:-5]
    part = ident_code[:-3]
    if int(vol) < 144:
        domen = 'https://basket-01.wb.ru'
    elif int(vol) < 288:
        domen = 'https://basket-02.wb.ru'
    elif int(vol) < 432:
        domen = 'https://basket-03.wb.ru'
    elif int(vol) < 720:
        domen = 'https://basket-04.wb.ru'
    elif int(vol) < 1008:
        domen = 'https://basket-05.wb.ru'
    elif int(vol) < 1062:
        domen = 'https://basket-06.wb.ru'
    elif int(vol) < 1116:
        domen = 'https://basket-07.wb.ru'
    elif int(vol) < 1170:
        domen = 'https://basket-08.wb.ru'
    elif int(vol) < 1314:
        domen = 'https://basket-09.wb.ru'
    elif int(vol) < 1601:
        domen = 'https://basket-10.wb.ru'
    else:
        domen = 'https://basket-11.wb.ru'

    return f'{domen}/vol{vol}/part{part}/{ident_code}'


def get_json_from_id(item_json):
    link = get_main_link(item_json)
    return f'{link}/info/ru/card.json'


def get_image_links(item_json):
    link = get_main_link(item_json)
    links = [f'{link}/images/big/{pic_num}.jpg' for pic_num in range(1, item_json['pics'] + 1)]
    return links


def get_items_from_query(query='pampers'):
    query = str(query).lower()
    count = 0
    items = []
    while True:
        count += 1
        print(f'********  PAGE {count}  ********')
        url = f'https://www.wildberries.ru/brands/{query}?sort=popular&page={count}'
        print(url)
        response = requests.get(url=url, headers=headers)
        if len(response.text) < 150:
            break
        items += response.json()['data']['products']
    print(f'Найдено {len(items)} позиций')

    return items


def get_items_from_brand(brand='pampers'):
    brand_json_url = f'https://static.wbstatic.net/data/brands/{str(brand).lower()}.json'
    print(brand_json_url)
    brand_id = requests.get(url=brand_json_url, headers=headers).json()['id']

    brand = str(brand).lower()
    count = 0
    items = []
    while True:
        count += 1
        print(f'********  PAGE {count}  ********')
        url = f'https://catalog.wb.ru/brands/p/catalog?appType=1&brand={brand_id}&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,-102269,-2162196,-1257786&emp=0&lang=ru&locale=ru&page={count}&pricemarginCoeff=1.0&reg=0&regions=80,64,83,4,38,33,70,82,69,68,86,75,30,40,48,1,22,66,31,71&sort=popular&spp=0'
        response = requests.get(url=url, headers=headers)
        if len(response.text) < 150:
            break
        items += response.json()['data']['products']
    print(f'Найдено {len(items)} позиций')

    return items


def get_photos_from_items(items):
    # Download photos
    for idx, item in enumerate(items):
        print(f'{idx + 1} из {len(items)}')
        ident = str(item['id'])
        folder_name = f'photos/{ident}'
        image_urls = get_image_links(item)
        for url in image_urls:
            jpeg_name = url.split('/')[-1]
            if not os.path.exists(folder_name + '/' + jpeg_name):  # Если файл еще не скачан
                Path(folder_name).mkdir(parents=True, exist_ok=True)
                response = requests.get(url, headers=headers)
                if response.status_code:
                    fp = open(folder_name + '/' + jpeg_name, 'wb')
                    fp.write(response.content)
                    fp.close()
                    print(url, 'ok')
                else:
                    print(url, 'не доступен')


if __name__ == '__main__':
    brand_input = input('Какой бренд выгрузить?\n')
    js_response = get_items_from_brand(brand_input)
    df = pd.DataFrame(js_response)
    try:
        df.colors = df.colors.apply(lambda x: ', '.join(sorted([item['name'] for item in x])))
    except Exception as e:
        print(f'Не удалось найти вкладку "colors" из-за ошибки {e}')
    df.to_excel(f'{brand_input}.xlsx', index=False)
