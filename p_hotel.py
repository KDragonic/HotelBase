import copy
import datetime
import json
import os
import re
import subprocess
import concurrent.futures
import sys
import traceback
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import time
import logging

# Настроки
simultaneous_parsing = 3

class MyLog:
    logger : logging.Logger

    def __init__(self, id) -> None:
        self.logger = self.create_logger(id)
        # subprocess.Popen(['python', 'print_log.py', f'r_logs/logger_{id}.log'], stdin=subprocess.PIPE)

    def create_logger(self, id):
        # создаем логгер
        logger = logging.getLogger(f"logger_{id}")
        handler = logging.FileHandler(filename=f'r_logs/logger_{id}.log', mode='w', encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        return logger

    def log(self, mes):
        self.logger.info(mes)

def split_list(lst, n):
    """
    Разделение списка на n подсписков примерно равной длины
    """
    size = len(lst) // n
    remainder = len(lst) % n
    result = []
    start = 0
    for i in range(n):
        end = start + size + (i < remainder)
        result.append(lst[start:end])
        start = end
    return result

def update_query_params(url, new_values):
    parsed_url = urlparse(url)
    query_dict = parse_qs(parsed_url.query)

    for key, value in new_values.items():
        query_dict[key] = value

    new_query = urlencode(query_dict, doseq=True)
    updated_url = urlunparse((parsed_url.scheme, parsed_url.netloc,
                             parsed_url.path, parsed_url.params, new_query, parsed_url.fragment))

    return updated_url

def create_webdriver():
    # Create a new instance of the Chrome driver
    chrome_options = webdriver.ChromeOptions()

    # Отключение загрузки картинок
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    # Отключение загрузки шрифтов и css
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-features=VizDisplayCompositor')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--disable-logging-redirect')
    chrome_options.add_argument('--disable-background-networking')
    chrome_options.add_argument('--disable-breakpad')
    chrome_options.add_argument('--disable-client-side-phishing-detection')
    chrome_options.add_argument('--disable-component-update')
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--disable-extensions-http-throttling')
    chrome_options.add_argument('--disable-extensions-file-access-check')
    chrome_options.add_argument('--disable-extensions-scheme-whitelist')
    chrome_options.add_argument('--disable-hang-monitor')
    chrome_options.add_argument('--disable-ipc-flooding-protection')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-prompt-on-repost')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('--disable-sync')
    chrome_options.add_argument('--disable-translate')
    chrome_options.add_argument('--metrics-recording-only')
    chrome_options.add_argument('--mute-audio')
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--safebrowsing-disable-auto-update')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-webgl')
    chrome_options.add_argument('--disable-threaded-animation')
    chrome_options.add_argument('--disable-threaded-scrolling')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-xss-auditor')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--ignore-certificate-errors')
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disk-cache=true')
    chrome_options.add_argument('--log-level=3')

    driver = webdriver.Chrome(chrome_options=chrome_options)

    # driver.request_interceptor = interceptor

    return driver

drivers = [create_webdriver() for i in range(simultaneous_parsing)]

def parser_hotel_rooms(url, driver, logger : MyLog):
    return_urls = []
    dates = [
            ["28.07.2023-01.08.2023", 4],
            ["28.08.2023-01.09.2023", 4],
            ["05.10.2023-08.10.2023", 3]
    ]

    retrun_rooms: dict[str, dict[str, list]] = {}

    additional_values = None

    operation_counter = 0
    operation_counter_max = 3 * 4

    for date, days in dates:
        for guests in range(1, 5):
            url = update_query_params(url, {"dates": date, "guests": guests})
            return_urls.append(url)
            operation_counter += 1

            if additional_values == None:
                additional_values, rooms = parser_room(
                    url, driver, True, date, days, guests)
            else:
                _, rooms = parser_room(url, driver, False, date, days, guests)

            logger.log(f"[{operation_counter}/{operation_counter_max}] {date} | {guests} => {len(rooms)}")
            # logging.info(f"[{operation_counter}/{operation_counter_max}] {date} | {guests} => {len(rooms)}")

            for key, val in rooms.items():
                if not retrun_rooms.get(key):
                    retrun_rooms[key] = {
                        "price": [],
                        "amenity": None,
                        "search": [],
                    }

                retrun_rooms[key]["price"].append(val["price"])
                retrun_rooms[key]["search"].append(val["search"])

                if retrun_rooms[key]["amenity"] == None:
                    retrun_rooms[key]["amenity"] = val["amenity"]

    # [Название] Цена | Гостей => Количество захваченных поисков
    logger.log(f"Информация об номерах [{len(retrun_rooms)}]:")
    for key, val in retrun_rooms.items():
        prices = [round(price["price"] / price["days"])
                  for price in val["price"]]
        max_price = max(prices)

        guests = [search["guests"] for search in val["search"]]
        max_guest = max(guests)

        logger.log(f"[{key}] ↑{max_price} | ↑{max_guest} => s{len(val['search'])}")

    return retrun_rooms, additional_values, return_urls

def parser_room(url, driver, get_additional_values: bool, date, days, guests):
    rooms: dict[str, list] = {}

    additional_values = None

    driver.get(url)

    # ждем полной загрузки страницы
    driver.execute_script("return document.readyState")

    scripts = driver.find_elements(
        "xpath", "//script[@type='text/javascript']")

    for script in scripts:
        try:
            driver.execute_script(script.get_attribute('innerHTML'))
        except:
            pass

    if additional_values == None:
        additional_values = {}
        try:
            title_stars = driver.find_element(
                By.CLASS_NAME, "zen-roomspage-title-stars")
            stars = title_stars.find_elements(
                By.CLASS_NAME, "zen-ui-stars-star")
            additional_values["stars_count"] = len(stars)
        except:
            additional_values["stars_count"] = 0

        try:
            span_time_in_out = driver.find_elements(
                By.CLASS_NAME, "PolicyBlock__policyTableCell_checkInCheckOut--sezvV")

            for obj in span_time_in_out:
                if obj.text.startswith("После"):
                    additional_values["time_in"] = obj.text.replace(
                        "После", "").strip()
                if obj.text.startswith("До"):
                    additional_values["time_out"] = obj.text.replace(
                        "До", "").strip()
            pass
        except:
            additional_values["time_in"] = "12:00"
            additional_values["time_out"] = "14:00"

        additional_values["title"] = driver.title

    try:
        # Ожидание появления элемента с классом zenroomspage-b2c-rates
        rates = WebDriverWait(driver, timeout=3).until(
            lambda d: d.find_elements(By.CLASS_NAME, "zenroomspage-b2c-rates"))
    except:
        rates = []

    for rate in rates:
        name = rate.find_element(
            By.CLASS_NAME, "zenroomspagerate-name-title").text
        name = name.replace("\n", " ")

        if not rooms.get(name):
            rooms[name] = {
                "price": None,
                "amenity": [],
                "search": None,
            }

        rooms[name]["search"] = {
            "date": {"start": date, "days": days}, "guests": guests}

        price = rate.find_elements(
            By.CLASS_NAME, "zenroomspage-b2c-rates-price-amount")[0].text
        price = int(price.replace(" ", "").replace("₽", ""))

        rooms[name]["price"] = {"price": price, "days": days}

        if len(rooms[name]["amenity"]) == 0:
            amenitys = rate.find_elements(
                By.CLASS_NAME, "zenroomspageroom-header-content-amenity")
            for amenity in amenitys:
                text_amenity = amenity.text
                rooms[name]["amenity"].append(text_amenity)

    return additional_values, rooms

def get_hotel(url_hotel, hotel_id, driver, logger : MyLog):
    start_time = int(time.time())

    url = "https://ostrovok.ru/hotel/search/v2/site/hp/content"
    params = {
        "lang": "ru",
        "hotel": hotel_id,
    }

    response = requests.get(url, params=params)
    json_data = response.json()

    amenities = {}

    for group in json_data["data"]["hotel"]["amenity_groups_v2"]:
        category = group["group_name"]
        amenities[category] = []
        for amenity in group["amenities"]:
            name = amenity["name"]
            amenities[category].append(name)

    address_parts = json_data["data"]["hotel"]["address"].split(', ')
    street = address_parts[0]
    house_number = address_parts[1]
    city = json_data["data"]["hotel"]["city"]
    country = json_data["data"]["hotel"]["country"]

    description = json_data["data"]["hotel"]["description"]

    images = []

    for img in json_data["data"]["hotel"]["images"]:
        w = img["width"]
        h = img["height"]

        url: str = img["tmpl"]

        url = url.replace("{size}", "1024x768")

        images.append({
            "url": url,
        })

    latitude = json_data["data"]["hotel"]["latitude"]
    longitude = json_data["data"]["hotel"]["longitude"]

    name = json_data["data"]["hotel"]["name"]

    rooms_data_parser_selenium, additional_data, return_urls = parser_hotel_rooms(
        url_hotel, driver, logger)

    rooms = []

    room_groups = json_data["data"]["hotel"]["room_groups"]

    for room in room_groups:
        if not rooms_data_parser_selenium.get(room["name"]):
            continue

        date_room = {
            "name": room["name"],
            "size": room.get("size"),
            "amenitie": [item for item in rooms_data_parser_selenium[room["name"]]["amenity"]],
            "search": rooms_data_parser_selenium[room["name"]]["search"],
            "visibility_area": {
                "date": [],
            },
            "rg_hash": room["rg_hash"],
        }

        days_list = [search["date"]["days"]
                     for search in rooms_data_parser_selenium[room["name"]]["search"]]
        guests = {
            "max": max(days_list) if days_list else None,
            "min": min(days_list) if days_list else None,
        }

        days_list = [search["date"]["days"]
                     for search in rooms_data_parser_selenium[room["name"]]["search"]]
        days = {
            "max": max(days_list) if days_list else None,
            "min": min(days_list) if days_list else None,
        }

        guests_list = [search["guests"]
                       for search in rooms_data_parser_selenium[room["name"]]["search"]]
        guests = {
            "max": max(guests_list) if guests_list else None,
        }

        date_room["visibility_area"]["days"] = days
        date_room["visibility_area"]["guests"] = guests

        date_room["imgs"] = []
        if rooms_data_parser_selenium.get(room["name"]):
            date_room["price"] = rooms_data_parser_selenium[room["name"]]["price"]
        else:
            date_room["price"] = 0

        for img in room["image_list_tmpl"]:
            w = img["width"]
            h = img["height"]

            url: str = img["src"]

            url = url.replace("{size}", "1024x768")

            date_room["imgs"].append({
                "url": url,
                "size": f"{w}x{h}",
            })

        rooms.append(date_room)

    end_time = int(time.time())

    hotel_data = {
        "debug": {
            "start_time": datetime.datetime.fromtimestamp(start_time).strftime("%d.%m.%Y %H:%M:%S"),
            "end_time": datetime.datetime.fromtimestamp(end_time).strftime("%d.%m.%Y %H:%M:%S"),
            "d_time_m": f"{round((end_time - start_time) / 60, 1)} минут",
            "d_time_s": f"{(end_time - start_time)} секунд",
        },
        "urls": return_urls,
        "name_hotel": name,
        "address": {
            "street": street,
            "house": house_number,
            "city": city,
            "continent": country,
        },
        "description": description,
        "images": images,
        "coordinates": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "description": description,
        "services": amenities,
        "rooms": rooms,
    }

    hotel_data.update(additional_data)

    logger.log(f"Скачался за {hotel_data['debug']['d_time_s']}")

    return hotel_data

urls = []

cities = {}
with open("slug.json", encoding='utf-8') as f:
    data = json.load(f)
    for slug in data:
        slug: str
        city = slug.split("/")[1]
        cities[city] = slug


if not os.path.exists("hotels/empty/"):
    os.mkdir("hotels/empty/")

if not os.path.exists("hotels/normal/"):
    os.mkdir("hotels/normal/")

# Цикл для чтения каждого файла в папке
for filename in os.listdir('cities/full'):
    if filename.endswith('.json'):
        with open(os.path.join('cities/full', filename), encoding='utf-8') as f:
            data = json.load(f)
            index, city = filename.split("_", 1)
            city = city.replace(".json", "")

            for hotel in data["hotels"]:
                slug = cities[city]
                obj = {
                    "city": city,
                    "url": f"https://ostrovok.ru/hotel/{slug}/mid9287753/{hotel['ota_hotel_id']}/?dates=20.09.2023-29.09.2023&guests=1",
                    "id_hotel": hotel['ota_hotel_id']
                }
                urls.append(obj)

index_urls = 0

there_are_already_hotels = []

for filename in os.listdir('hotels'):
    if filename.endswith('.json'):
        there_are_already_hotels.append(filename.split(".")[0])


def find_files(path, extension):
    list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                list.append(file.split(".")[0])

    return list


there_are_already_hotels = find_files("hotels", '.json')

print(f"Уже скачено {len(there_are_already_hotels)} отелей, нужно ещё {len(urls) - len(there_are_already_hotels)} скачать")

if not os.path.exists("r_logs/"):
    os.mkdir("r_logs/")

def while_hotel(urls, id, mixing_id, there_are_already_hotels, driver):
    """Основной цикт получения отелей

    Args:
        `urls` (list): Список с url и slug\n
        `id` (int): ID цикла\n
        `mixing_id` (int): Смешение вывода index_urls\n
        `there_are_already_hotels` (list): Отели который уже скачены
    """
    logger = MyLog(id)
    index_urls = 0
    while index_urls < len(urls):
        try:
            url = urls[index_urls]

            if url["id_hotel"] in there_are_already_hotels:
                index_urls += 1
                logger.log(f"[{index_urls+mixing_id}/{len(urls)+mixing_id}] {url['id_hotel']} уже есть")
                # logger.log(f"[{index_urls+mixing_id}/{len(urls)}] {url['id_hotel']} уже есть")
                continue

            logger.log(f"[{index_urls+mixing_id+1}/{len(urls)+mixing_id}] {url['city']} => {url['id_hotel']} скачивается")
            # logger.log(
            #     f"[{index_urls+mixing_id+1}/{len(urls)+mixing_id}] {url['city']} => {url['id_hotel']} скачивается")

            data = get_hotel(url["url"], url["id_hotel"], driver, logger)

            index_urls += 1

            if len(data["rooms"]) == 0:
                path_dir = f"hotels/empty/{url['city']}/"
            else:
                path_dir = f"hotels/normal/{url['city']}/"

            if not os.path.exists(path_dir):
                os.mkdir(path_dir)

            with open(os.path.join(path_dir, f"{url['id_hotel']}.json"), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
                logger.log(f"{os.path.join(path_dir, url['id_hotel'] + '.json')} записан в файл")
                # logger.log(f"{url['id_hotel']} записан в файл")
        except:
            error_type, error_value, tb = sys.exc_info()
            traceback_msg = "".join(traceback.format_tb(tb))
            error = f"{error_type.__name__} - {error_value}\n {traceback_msg}"
            # logger.log(error)
            logger.log(error)

splitted_url = split_list(urls, simultaneous_parsing)

with concurrent.futures.ThreadPoolExecutor(max_workers=simultaneous_parsing) as executor:
    futures = [executor.submit(while_hotel, splitted_url[i], i, round(i*(len(urls) / simultaneous_parsing)), there_are_already_hotels, drivers[i]) for i in range(simultaneous_parsing)]
