#!/usr/bin/env python

import math
from operator import itemgetter
from time import sleep
import requests

import utils

CATEGORIES = {
    "xbox360": 782,
    "psp": 767,
    "ps4": 1021,
    "switch": 1038,
    "xboxone": 1023,
}

STORES = {
    'phoniex': 2010,
    'forum': 2027,
    'vr': 2037,
}

def get_games(category_id, store_id):
    first_record = 1
    count = 50
    # we get the total records only after the first request
    # so let's set this to a arbitrarily high number.
    total_records = 999999999999999
    games = []
    while first_record < total_records:
        print(f'starting at {first_record}')
        url = (
            f"https://wss2.cex.in.webuy.io/v3/boxes?"
            f"categoryIds=[{category_id}]&firstRecord={first_record}"
            f"&count={count}&storeIds=[{store_id}]"
            "&sortBy=sellprice&sortOrder=asc"
        )

        response = requests.get(url)
        response.raise_for_status()
        response_json = response.json()
        data = response_json['response']['data']
        total_records = data['totalRecords']
        print(f"total_records => {data['totalRecords']}")
        for box in data['boxes']:
            game_title = box['boxName']
            game_price = box['sellPrice']
            game_url = f"https://in.webuy.com/product-detail?id={box['boxId'].lower()}"
            # lets filter out ntsc games,
            # since that wont work with our console
            if 'ntsc' not in game_title.lower():
                games.append({
                    'url': game_url,
                    'title': game_title,
                    'price': game_price
                })
        first_record = first_record + count
        sleep(1)
    return games

def generate():
    category_names = CATEGORIES.keys()
    store_names = STORES.keys()
    for store_name in store_names:
        for category_name in category_names:
            print(f'{store_name} => {category_name}')
            category_id = CATEGORIES[category_name]
            store_id = STORES[store_name]
            games = get_games(category_id, store_id)
            if games:
                utils.generate_csv(f'cex-{store_name}-{category_name}', games, ['title', 'price', 'url'])
                utils.generate_html(f'cex-{store_name}-{category_name}', games)

if __name__ == '__main__':
    generate()