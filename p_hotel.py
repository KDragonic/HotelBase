import datetime
import json
import os
import re
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

logging.basicConfig(filename= "logs/" + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".log", level=logging.INFO, encoding='utf-8', format='[%(asctime)s][%(levelname)s] %(message)s')


def generate_date_list(days):
    list = map(lambda x: datetime.datetime.strptime(x, "%d.%m.%Y"), ["08.09.2023", "12.09.2023", "16.09.2023"])

    return list


def generate_date_range(start_day, days):
    first_day = start_day
    second_day = first_day + datetime.timedelta(days=days)
    date_range = first_day.strftime(
        '%d.%m.%Y') + '-' + second_day.strftime('%d.%m.%Y')

    return date_range


def update_query_params(url, new_values):
    parsed_url = urlparse(url)
    query_dict = parse_qs(parsed_url.query)

    for key, value in new_values.items():
        query_dict[key] = value

    new_query = urlencode(query_dict, doseq=True)
    updated_url = urlunparse((parsed_url.scheme, parsed_url.netloc,
                             parsed_url.path, parsed_url.params, new_query, parsed_url.fragment))

    return updated_url


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

#Включаем кеш
chrome_options.add_argument('--disk-cache-size=33554432')
chrome_options.add_argument('--media-cache-size=33554432')

#Выключить лишние логи
chrome_options.add_argument('--log-level=3')

# Создание экземпляра драйвера
driver = webdriver.Chrome(chrome_options=chrome_options)

def get_selenium_data(url):
    dates = generate_date_list(3)
    rooms: dict[str, list] = {}

    additional_values = None

    operation_counter = 0
    operation_counter_max = 3 * 4
    days = 4

    for date in dates:
            for guests in range(1, 5):
                url = update_query_params(url, {"dates": generate_date_range(date, days), "guests": guests})

                operation_counter += 1

                driver.get(url)

                driver.execute_script("return document.readyState") # ждем полной загрузки страницы

                scripts = driver.find_elements("xpath", "//script[@type='text/javascript']")

                for script in scripts:
                    try:
                        driver.execute_script(script.get_attribute('innerHTML'))
                    except:
                        pass

                if additional_values == None:
                    additional_values = {}
                    try:
                        title_stars = driver.find_element(By.CLASS_NAME, "zen-roomspage-title-stars")
                        stars = title_stars.find_elements(By.CLASS_NAME, "zen-ui-stars-star")
                        additional_values["stars_count"] = len(stars)
                    except:
                        additional_values["stars_count"] = 0

                    try:
                        span_time_in_out = driver.find_elements(By.CLASS_NAME, "PolicyBlock__policyTableCell_checkInCheckOut--sezvV")

                        for obj in span_time_in_out:
                            if obj.text.startswith("После"):
                                additional_values["time_in"] = obj.text.replace("После", "").strip()
                            if obj.text.startswith("До"):
                                additional_values["time_out"] = obj.text.replace("До", "").strip()
                        pass
                    except:
                        additional_values["time_in"] = "12:00"
                        additional_values["time_out"] = "14:00"

                    additional_values["title"] = driver.title



                try:
                    # Ожидание появления элемента с классом zenroomspage-b2c-rates
                    rates = driver.find_elements(By.CLASS_NAME, "zenroomspage-b2c-rates")
                except:
                    rates = []

                # rates = driver.find_elements(By.CLASS_NAME, "zenroomspage-b2c-rates")

                for rate in rates:
                    name = rate.find_element(By.CLASS_NAME, "zenroomspagerate-name-title").text
                    name = name.replace("\n", " ")

                    if not rooms.get(name):
                        rooms[name] = {
                            "price": [],
                            "amenity": [],
                            "search": [],
                        }

                    rooms[name]["search"].append({"date": {"start": date.strftime("%d.%m.%Y"), "days": days}, "guests": guests})

                    price = rate.find_elements(By.CLASS_NAME, "zenroomspage-b2c-rates-price-amount")[0].text
                    price = int(price.replace(" ", "").replace("₽", ""))

                    rooms[name]["price"].append({"price": price, "days": days})

                    if len(rooms[name]["amenity"]) == 0:
                        amenitys = rate.find_elements(By.CLASS_NAME, "zenroomspageroom-header-content-amenity")
                        for amenity in amenitys:
                            text_amenity = amenity.text
                            rooms[name]["amenity"].append(text_amenity)

                print(f"({operation_counter}/{operation_counter_max}) Комнаты получены на дату {date.strftime('%d.%m.%Y')} и дней {days}, на {guests} гостей\t\t\t", end="\r")
                logging.info(f"({operation_counter}/{operation_counter_max}) Комнаты получены на дату {date.strftime('%d.%m.%Y')} и дней {days}, на {guests} гостей")


    return rooms, additional_values


def get_additional_values(url):
    content = {}
    driver = webdriver.Chrome()

    driver.get(url)
    driver.execute_script("return document.readyState") # ждем полной загрузки страницы

    # scripts = driver.find_elements_by_xpath("//script[@type='text/javascript']")
    scripts = driver.find_elements("xpath", "//script[@type='text/javascript']")

    for script in scripts:
        driver.execute_script(script.get_attribute('innerHTML'))

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    try:
        title_stars = driver.find_element(By.CLASS_NAME, "zen-roomspage-title-stars")
        stars = title_stars.find_elements(By.CLASS_NAME, "zen-ui-stars-star")
        content["stars_count"] = len(stars)
    except:
        content["stars_count"] = 0

    try:
        span_time_in_out = driver.find_elements(By.CLASS_NAME, "PolicyBlock__policyTableCell_checkInCheckOut--sezvV")

        for obj in span_time_in_out:
            if obj.text.startswith("После"):
                content["time_in"] = obj.text.replace("После", "").strip()
            if obj.text.startswith("До"):
                content["time_out"] = obj.text.replace("До", "").strip()
        pass
    except:
        content["time_in"] = "12:00"
        content["time_out"] = "14:00"

    content["title"] = driver.title

    return content

def get_hotel(url_hotel, hotel_id):
    parsed_url = urlparse(url_hotel)
    parsed_query = parse_qs(parsed_url.query)
    hotel_param = parsed_url.path.split('/')[-2]

    start_time = int(time.time())

    url = "https://ostrovok.ru/hotel/search/v2/site/hp/content"
    params = {
        "lang": "ru",
        "hotel": hotel_param,
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
            "size": f"{w}x{h}",
        })

    latitude = json_data["data"]["hotel"]["latitude"]
    longitude = json_data["data"]["hotel"]["longitude"]

    name = json_data["data"]["hotel"]["name"]

    rooms_data_parser_selenium, additional_data = get_selenium_data(url_hotel)

    rooms = []

    room_groups = json_data["data"]["hotel"]["room_groups"]

    pattern = r"\\d{1,2}\\s*[мM][2²]"

    for room in room_groups:
        if not rooms_data_parser_selenium.get(room["name"]):
            continue

        date_room = {
            "name": room["name"],
            "size": room.get("size"),
            "amenitie": [item for item in rooms_data_parser_selenium[room["name"]]["amenity"] if not re.search(pattern, item)],
            "search": rooms_data_parser_selenium[room["name"]]["search"],
            "visibility_area": {
                "date": [],
            },
            "rg_hash": room["rg_hash"],
        }

        days_list = [search["date"]["days"] for search in rooms_data_parser_selenium[room["name"]]["search"]]
        guests = {
            "max": max(days_list) if days_list else None,
            "min": min(days_list) if days_list else None,
        }

        days_list = [search["date"]["days"] for search in rooms_data_parser_selenium[room["name"]]["search"]]
        days = {
            "max": max(days_list) if days_list else None,
            "min": min(days_list) if days_list else None,
        }

        guests_list = [search["guests"] for search in rooms_data_parser_selenium[room["name"]]["search"]]
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

    print(f"Скачался за {hotel_data['debug']['d_time_s']}", end="                                                                   \n")
    logging.info(f"Скачался за {hotel_data['debug']['d_time_s']}")

    return hotel_data

urls = []

cities = {}
with open("slug.json", encoding='utf-8') as f:
    data = json.load(f)
    for obj in data:
        cities[obj["city"]] = obj["slug"]

# Цикл для чтения каждого файла в папке
for filename in os.listdir('cities'):
    if filename.endswith('.json'):
        with open(os.path.join('cities', filename), encoding='utf-8') as f:
            data = json.load(f)
            index, city = filename.split("_")
            city = city.split(".")[0]

            for hotel in data["hotels"]:
                slug = cities[city]
                obj = {
                    "url": f"https://ostrovok.ru/hotel/{slug}/mid9287753/{hotel['ota_hotel_id']}/?dates=20.09.2023-29.09.2023&guests=1",
                    "id_hotel": hotel['ota_hotel_id']
                }
                urls.append(obj)

with open("slug.json", encoding='utf-8') as f:
    data = json.load(f)
    for obj in data:
        cities[obj["city"]] = obj["slug"]

index_urls = 0

there_are_already_hotels = []

for filename in os.listdir('hotels'):
    if filename.endswith('.json'):
        there_are_already_hotels.append(filename.split(".")[0])

print(f"Уже скачено {len(there_are_already_hotels)} отелей, нужно ещё {len(urls) - len(there_are_already_hotels)} скачать")

while index_urls < len(urls):
    try:
        url = urls[index_urls]

        if url["id_hotel"] in there_are_already_hotels:
            index_urls += 1
            print(f"\033[0;32m{url['id_hotel']}\033[0m уже есть")
            logging.info(f"{url['id_hotel']} уже есть")
            continue

        print(f"\033[0;33m{url['id_hotel']}\033[0m скачивается")
        logging.info(f"{url['id_hotel']} скачивается")

        data = get_hotel(url["url"], url["id_hotel"])

        index_urls += 1

        with open(f'hotels/{url["id_hotel"]}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            logging.info(f"{url['id_hotel']} записан в файл")
    except:
        error_type, error_value, tb = sys.exc_info()
        traceback_msg = "".join(traceback.format_tb(tb))
        error = f"{error_type.__name__} - {error_value}\n {traceback_msg}"
        logging.error(error)
        print("\033[31m" + error + "\033[0m")