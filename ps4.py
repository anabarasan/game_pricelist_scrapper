#!/usr/bin/env python

import math
from operator import itemgetter
from time import sleep
from bs4 import BeautifulSoup
import requests

import utils

PS_STORE = "https://store.playstation.com"
PS4_STORE = "/en-in/grid/STORE-MSF75508-PS4CAT"
# STORE_FILTERS = "platform=ps4&price=0-0%2C0-99%2C100-149%2C150-249%2C250-499"
STORE_FILTERS = "platform=ps4"

def get_game_details(game_details_container):
    container = game_details_container.find("div", class_="grid-cell__body")
    title_container = container.find("div", class_="grid-cell__title")
    game_title = title_container.find("span").get_text().strip()
    game_url = container.find("a", class_="internal-app-link")["href"]
    game_url = f"{PS_STORE}{game_url}"
    price_container = container.find("h3", class_="price-display__price")
    if price_container:
        game_price = price_container.get_text().strip()
    else:
        grid_footer = container.find("div", class_="grid-cell__footer")
        game_price = grid_footer.get_text().strip() if grid_footer else "-2"
    game_price = game_price.replace("Rs", "").replace(",", "")
    try:
        game_price = float(game_price)
    except ValueError:
        game_price = 0.0 if game_price == "Free" else -1.0
    # print((f"{game_title} \t {game_price} \t "
    #        f"{'PreOrder maybe?!' if game_price == -2.0 else ''}"))
    return {"title": game_title, "price": game_price, "url": game_url}

def get_page_count(page):
    matches_range = page.find("span", class_="range")
    matches_container = matches_range.find_parent("div")
    page_range = matches_range.get_text()
    matches = matches_container.get_text().replace(
        page_range, "").replace("of", "").replace("Matches", "")
    total_no_of_items = int(matches.strip())
    item_range = page_range[page_range.find("-")+1:].strip()
    item_range = int(item_range)
    # print("Total Number of Items =>", total_no_of_items)
    # print("Page Range => ", item_range)
    page_count = total_no_of_items / item_range
    # print("Calculated Page Count => ", page_count)
    page_count = math.ceil(page_count)
    # print("Actual Page Count => ", page_count)
    # print("\n")
    return page_count

def generate():
    page_count = 10
    page_num = 1
    game_list = []
    while page_num <= page_count:
        print(f"\n__PS4__ Page No: {page_num}\n")
        try:
            url = f"{PS_STORE}/{PS4_STORE}/{page_num}?{STORE_FILTERS}"
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            if page_num == 1:
                page_count = get_page_count(soup)

            games = soup.find_all("div", class_="grid-cell--game")
            for game in games:
                game_list.append(get_game_details(game))
            page_num += 1
            sleep(1)
            # break
        except Exception as e:
            print(e)
            sleep(5)
            print(f"failed on page no {page_num}, retrying...")

    #sort by price
    game_list = sorted(game_list, key=itemgetter("price"))

    utils.generate_csv("ps4", game_list, ["title", "price", "url"])
    utils.generate_html("ps4", game_list)

if __name__ == '__main__':
    generate()
