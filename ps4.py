#!/usr/bin/env python

import json
import math
from operator import attrgetter
from time import sleep

from bs4 import BeautifulSoup
import requests

import utils

# PS_STORE = "https://store.playstation.com"
# PS4_STORE = "/en-in/grid/STORE-MSF75508-PS4CAT"
# # STORE_FILTERS = "platform=ps4&price=0-0%2C0-99%2C100-149%2C150-249%2C250-499"
# STORE_FILTERS = "platform=ps4"
BASE_URL = "https://store.playstation.com"
PS4_CATEGORY_ID = "44d8bb20-653e-431e-8ad0-c0a365f68d2f"

def get_page_count(pageInfo):
    total_count = pageInfo["totalCount"]
    page_size = pageInfo["size"]
    page_count = total_count / page_size
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
        print(f"__PS4__ Page No: {page_num}")
        try:
            response = requests.get(f"{BASE_URL}/en-in/category/{PS4_CATEGORY_ID}/{page_num}")
            soup = BeautifulSoup(response.content, 'html.parser')
            next_data = soup.find("script", {"id": "__NEXT_DATA__"})
            data = json.loads(next_data.string)["props"]["apolloState"]
            root_query = data["ROOT_QUERY"]
            for key, value in root_query.items():
                if value['typename'] == "CategoryGrid":
                    CategoryGridId = value["id"]
                    break

            CategoryGrid = data[CategoryGridId]
            pageInfoId = CategoryGrid["pageInfo"]["id"]
            products = CategoryGrid["products"]

            pageInfo = data[pageInfoId]
            if page_num == 1:
                page_count = get_page_count(pageInfo)
                print(f"__PS4__ total_pages = {page_count}")
            isLast = data[pageInfoId]["isLast"]
            if isLast:
                print(f"__PS4__ Last Page")
                break

            for product in products:
                try:
                    productId = product["id"]
                    productInfo = data[productId]
                    name = productInfo["name"]
                    gameid = productInfo["id"]
                    priceId = productInfo["price"]["id"]
                    priceInfo = data[priceId]
                    price = "0" if priceInfo["isFree"] else priceInfo["discountedPrice"]
                    price = "-1" if price == "Unavailable" else price
                    original_price = "0" if priceInfo["isFree"] else priceInfo["basePrice"]
                    original_price = "-1" if original_price == "Unavailable" else original_price
                    price = float(price.replace("Rs ", "").replace(",", ""))
                    original_price = float(original_price.replace("Rs ", "").replace(",", ""))
                    url = f"{BASE_URL}/en-in/product/{gameid}"
                    game = utils.Game(name, "", price, url, original_price=original_price)
                    # print(game)
                    game_list.append(game)
                except Exception as e:
                    print("__PS4__ ", e)
                    print("__PS4__ ProductId: ", productId)
                    print("__PS4__ PriceId: ", priceId)
                    raise
            page_num += 1
            sleep(1)
            # break
        except Exception as e:
            print("__PS4__", e)
            sleep(5)
            print(f"__PS4__ failed on page no {page_num}, retrying...")

    #sort by price
    game_list = sorted(game_list, key=attrgetter("price"))

    utils.generate_csv("ps4", game_list, ["title", "price", "url"])
    utils.generate_html("ps4", game_list)

if __name__ == '__main__':
    generate()
