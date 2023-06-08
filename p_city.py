import json
import os
import re
from time import sleep
from seleniumwire import webdriver  # Import from seleniumwire
from seleniumwire.utils import decode
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
# driver = webdriver.Chrome()

def interceptor(request):
    # Block PNG, JPEG and GIF images
    if request.path.endswith(('.png', ".jpeg", '.jpg', '.gif')):
        request.abort()

driver.request_interceptor = interceptor

def get_ajaxs_url(url):
    global no_full_hotels_list
    del driver.requests
    body_obj = None
    body = None
    print("\tПолучение отелей:")
    while (True):
        try:
            driver.get(url)

            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_all_elements_located)

            for req in driver.requests:
                if req.response:
                    if re.search("hotel/search/v2/site/serp\?session\=", req.url):
                        # try:
                            body = decode(req.response.body, req.response.headers.get('Content-Encoding', 'identity')).decode('utf-8')
                            body_obj = json.loads(body)
                            search_finished = body_obj["search_finished"]
                            if search_finished == True:
                                print(f"\t\t\033[0;32mОтелей {body_obj['total_av_hotels']} (Все)\033[0m")
                                return body_obj
                            else:
                                if len(no_full_hotels_list) < len(body_obj["map_hotels"]):
                                    no_full_hotels_list = body_obj["map_hotels"]

                                print(f"\t\t\033[0;33mОтелей {body_obj['total_av_hotels']} (Не полный)\033[0m")
                        # except:
                        #     print("\t\t\033[0;31mОшибка декодирования\033[0m")

            print("\t\t\033[0;31mНу удалость найти запрос финального поиска\033[0m")
            break
        except Exception as ex:
            print("\t\t\033[0;31mОшибка получения запросов\033[0m")
            print(ex)

    print("\t\t\033[0;31mНе получены отели\033[0m")
    return None

cities = []

with open("slug.json", encoding="utf-8") as json_file:
    data = json.load(json_file)
    cities = [{"city": obj.split("/")[1], "slug": obj} for obj in data]


verification_list_cities_slug = []
verification_list_cities = []

index_city = 0

attempt = 0

files_list = []

if not os.path.exists("cities/"):
    os.mkdir("cities/")

for filename in os.listdir("cities"):
    if filename.endswith(".json"):
        with open("cities/" + filename, encoding="utf-8") as json_file:
            data = json.load(json_file)
            files_list.append(data["city"]["slug"])

no_full_hotels_list = []
no_full_index = 0

if not os.path.exists("cities/full/"):
    os.mkdir("cities/full/")

if not os.path.exists("cities/no_full/"):
    os.mkdir("cities/no_full/")

if not os.path.exists("cities/empty/"):
    os.mkdir("cities/empty/")

while index_city < len(cities):
    if no_full_index != index_city:
        no_full_hotels_list = []
        no_full_index = index_city


    if cities[index_city]['slug'] in files_list:
        index_city += 1
        continue

    city = cities[index_city]
    url = f"https://ostrovok.ru/hotel/{city['slug']}/?guests=1&map=true?distance=999&dates=01.10.2023-04.10.2023&guests=1&price=one&type_group=hostel.hotel.apart_hotel.guesthouse.camping.glamping"

    if attempt <= 0:
        print(f"Запущен: {index_city + 1} -> {city['city']} -> https://ostrovok.ru/hotel/{city['slug']}/")
    else:
        print(f"\t\033[0;33mПопытка {attempt}: {index_city + 1} -> {city['city']} -> https://ostrovok.ru/hotel/{city['slug']}/\033[0m")

    data_row = get_ajaxs_url(url)

    if data_row == None:
        if attempt < 30:
            attempt += 1

            #Что за 10 попыток не получен ни один отель
            if attempt > 10 and len(no_full_hotels_list) <= 0:
                print(f"\t\033[0;31mНеудача: за 10 попыток не получен ни один отель\033[0m")
                attempt = 0
                index_city += 1

                path = f"cities/empty/{index_city}_{city['city']}.json"
                with open(path, "w", encoding="utf-8") as file:
                    obj_json = {
                        "city": city,
                        "count": 0,
                        "hotels": [],
                        "url": url,
                        "full_hotels_list": False,
                    }
                    json.dump(obj_json, file, ensure_ascii=False)

                continue

            time_sleep = attempt * 0.2 if attempt <= 10 else 2
            sleep(time_sleep)
            continue
        else:
            attempt = 0
            index_city += 1
            print(f"\t\033[0;31mНеудача: за 30 попыток не удалось получить отели\033[0m")

            if len(no_full_hotels_list) <= 0:
                path = f"cities/empty/{index_city}_{city['city']}.json"
                with open(path, "w", encoding="utf-8") as file:
                    obj_json = {
                        "city": city,
                        "count": 0,
                        "hotels": [],
                        "url": url,
                        "full_hotels_list": False,
                    }
                    json.dump(obj_json, file, ensure_ascii=False)

                continue

    if len(no_full_hotels_list) > 0:
        print(f"\t\033[0;33mНе полный список отелей сохранён из {len(no_full_hotels_list)} отелей\033[0m")
    else:
        print(f"\t\033[0;32mУдача: Отелей {len(data_row['map_hotels'])}\033[0m")

    attempt = 0

    index_city += 1

    hotels_list = []

    hotels = []

    is_full_hotels_list = True

    if data_row == None:
        if len(no_full_hotels_list) > 0:
            hotels = no_full_hotels_list
            is_full_hotels_list = False
    else:
        hotels = data_row["map_hotels"]


    if len(hotels) == 0:
        path = f"cities/empty/{index_city}_{city['city']}.json"
        with open(path, "w", encoding="utf-8") as file:
            obj_json = {
                "city": city,
                "count": 0,
                "hotels": [],
                "url": url,
                "full_hotels_list": False,
            }
            json.dump(obj_json, file, ensure_ascii=False)
            
            print(f"\t\033[0;32mФайл создан успеншо: {index_city}_{city['city']}.json\033[0m")
            continue

    for hotel in hotels:
        obj = {
            "ota_hotel_id": hotel.get("ota_hotel_id"),
            "master_id": hotel.get("ota_hotel_id"),
            "latitude": hotel.get("latitude"),
            "longitude": hotel.get("longitude"),
            "rating": hotel.get("rating"),
            "price": hotel.get("price"),
        }

        hotels_list.append(obj)

    if len(hotels_list) > 0:
        if is_full_hotels_list:
            path = f"cities/full/{index_city}_{city['city']}.json"
        else:
            path = f"cities/no_full/{index_city}_{city['city']}.json"

        with open(path, "w", encoding="utf-8") as file:
            try:
                obj_json = {
                    "city": city,
                    "count": len(hotels_list),
                    "hotels": hotels_list,
                    "url": url,
                    "full_hotels_list": is_full_hotels_list,
                }
                json.dump(obj_json, file, ensure_ascii=False)

                print(f"\t\033[0;32mФайл создан успеншо: {index_city}_{city['city']}.json\033[0m")
            except:
                print(f"\t\033[0;31mОшибка: файл не был создан {index_city}_{city['city']}.json\033[0m")



