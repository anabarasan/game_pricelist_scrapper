#!/usr/bin/env python

import math
from operator import attrgetter
from time import sleep
from bs4 import BeautifulSoup
import requests

import utils

MARKET_PLACE = 'https://marketplace.xbox.com'
BASE_URL = f'{MARKET_PLACE}/en-IN/Games/Xbox360Games?pagesize=90&SortBy=Title&Page='
BASE_URL = f'{MARKET_PLACE}/en-IN/Games/All?pagesize=90&SortBy=Title&Page='
RETRIES = 5

def get_page_count():
    try:
        # print('Getting Page Count.')
        url = BASE_URL + str(1)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        coverage = soup.find_all('div', class_='Coverage')
        game_count = coverage[0].get_text().split(' of ')[1]
        page_count = math.ceil(int(game_count.replace(",", "")) / 90)
        return page_count
    except Exception as e:
        print("__XBOX360__", e)
        sleep(5)
        print("__XBOX360__ Retrying.... ")
        get_page_count()


def get_game_details(game_url, tries=1):
    try:
        game_page = requests.get(game_url, timeout=30)
    except Exception as e:
        print("__XBOX360__", e, game_url)
        if tries == RETRIES:
            return 'unknown', -1.0
        else:
            return get_game_details(game_url, tries+1)
    soup = BeautifulSoup(game_page.content, 'html.parser')
    sleep(1)
    game_title = soup.find_all('h1')[0].get_text().strip()
    try:
        price = soup.find_all('span', class_='SilverPrice')[0].get_text()
        price = 0 if price == 'Free' else float(price.replace('Rs.', '').replace(',', ''))
    except IndexError:
        print('__XBOX360__ IndexError', game_url)
        if tries == RETRIES:
            price = -1.0
        else:
            game_title, price = get_game_details(game_url, tries+1)
    return game_title, price


def generate():
    page_count = get_page_count()
    page_no = 1
    game_list = []
    while page_no <= page_count:
        print(f"__XBOX360__ Page No: {page_no}")
        try:
            url = BASE_URL + str(page_no)
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            games = soup.find_all('a', class_='Game')
            for game in games:
                game_url = f"{MARKET_PLACE}{game['href']}"
                game_title, price = get_game_details(game_url)
                game_detail = utils.Game(game_title, "", price, game_url)
                # print(game_title, price)
                game_list.append(game_detail)
            page_no += 1
        except Exception as e:
            print("__XBOX360__", e)
            sleep(5)
            print(f'__XBOX360__ failed on page no {page_no}, retrying...')

    #sort by price
    game_list = sorted(game_list, key=attrgetter('price'))

    utils.generate_html('xbox360', game_list)
    utils.generate_csv('xbox360', game_list, ['title', 'price', 'url'])
    utils.publish()

if __name__ == '__main__':
    generate()
