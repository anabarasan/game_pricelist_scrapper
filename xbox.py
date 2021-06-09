#!/usr/bin/env python3
import argparse
from operator import attrgetter, itemgetter
import os
from time import sleep

from bs4 import BeautifulSoup
from lxml import etree, html
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

import utils

INITIAL_WAIT_TIME = 15
AJAX_WAIT_TIME = 5
GAME_LIST = []

CATALOGUE_URL = "https://www.xbox.com/en-in/games/all-games"
XPATH_TOTAL_GAMES = "/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]/div[1]/p"
XPATH_CATALOGUE = '//*[@id="ContentBlockList_1"]/div[1]/div[2]/div[4]'
XPATH_NEXT_PAGE = '/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/nav/ul/li[13]'
XPATH_NEXT_PAGE_LINK = '/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/nav/ul/li[13]/a'
XPATH_GAMES_PER_PAGE_MENU = '/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[6]/section/div/div/button'
XPATH_GAMES_PER_PAGE_200 = '/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]/div[6]/section/div/div/ul/li[4]'

def get_driver(headless=True, incognito=True):
    chrome_options = webdriver.ChromeOptions()
    if incognito:
        chrome_options.add_argument("--incognito")
    if headless:
        chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver

def get_total_available_games(driver):
    sleep(INITIAL_WAIT_TIME)
    total_games_text = driver.find_element_by_xpath(XPATH_TOTAL_GAMES)
    total_games_text = total_games_text.get_attribute("innerHTML")
    total_games = total_games_text.split(" of ")[1].split(" ")[0]
    return total_games

def set_max_games_per_page(driver):
    driver.find_element_by_xpath(XPATH_GAMES_PER_PAGE_MENU).click()
    driver.find_element_by_xpath(XPATH_GAMES_PER_PAGE_200).click()
    sleep(AJAX_WAIT_TIME)

def process_game_item(page):
    try:
        soup = BeautifulSoup(page, 'html.parser')
        game_link = soup.find('a', class_='gameDivLink')['href']
        h3 = soup.find('h3')
        name = h3.get_text()
        span_textpricenew = soup.find('span', class_='textpricenew')
        price = span_textpricenew.get_text() if span_textpricenew else "-1"
        price = float(price.replace("₹", "").replace(",", ""))
        s_tag = soup.find('s')
        original_price = s_tag.get_text() if s_tag else 0
        span_c_badges = soup.find_all('span', class_='c-badge')
        badges = [span.get_text().strip() for span in span_c_badges]
        description = soup.find('div', class_='popdescription')
        description = description.get_text().replace("Description: ", "").strip() if description else ""
        game = utils.Game(name, description, price, game_link, badges, original_price)
        GAME_LIST.append(game)
    except:
        print("__XBOX__", page)
        raise

def read_catalogue_page(driver):
    catalogue = driver.find_element_by_xpath(XPATH_CATALOGUE)
    content = catalogue.get_attribute("outerHTML")
    tree = html.fromstring(content)
    products = tree.xpath("//div[contains(@class, 'm-product-placement-item')]")
    # print("finding games")
    for product in products:
        product_item_html = etree.tostring(product, pretty_print=True)
        process_game_item(product_item_html)

def next_page(driver):
    try:
        driver.find_element_by_link_text("Next").click()
        sleep(AJAX_WAIT_TIME)
        return True
    except NoSuchElementException:
        return False

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_false", default=True)
    args = parser.parse_args()
    return args

def generate():
    args = parse_args()
    with get_driver(headless=args.debug) as driver:
        driver.get(CATALOGUE_URL)
        total_games = get_total_available_games(driver)
        set_max_games_per_page(driver)
        print("__XBOX__ Number of Games in Catalogue:", total_games)
        next_page_available = True
        page_no = 1
        while next_page_available:
            print(f"__XBOX__ Page No: {page_no}")
            read_catalogue_page(driver)
            next_page_available = next_page(driver)
            page_no += 1

    #sort by price
    GAME_LIST.sort(key=attrgetter('name'))
    utils.generate_html('xbox', GAME_LIST)
    utils.generate_csv('xbox', GAME_LIST, ['title', 'price', 'url'])

if __name__ == "__main__":
    generate()
