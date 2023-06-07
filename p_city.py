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

    print("\t\t\033[0;31mНе получилось получить отели\033[0m")
    return None



citys = [
    {
        "city": "Москва",
        "slug": "russia/moscow"
    },
    {
        "city": "Санкт-Петербург, Северо-Западный федеральный округ",
        "slug": "russia/st._petersburg"
    },
    {
        "city": "Новосибирская область",
        "slug": "russia/western_siberia_novosibirsk_oblast_multi"
    },
    {
        "city": "Свердловская область",
        "slug": "russia/ural_sverdlovsk_oblast_multi"
    },
    {
        "city": "Республика Татарстан",
        "slug": "russia/volga_region_republic_of_tatarstan_multi"
    },
    {
        "city": "Нижегородская область",
        "slug": "russia/volga_region_nizhny_novgorod_oblast_multi"
    },
    {
        "city": "Челябинская область",
        "slug": "russia/ural_chelyabinsk_oblast_multi"
    },
    {
        "city": "Красноярский край",
        "slug": "russia/western_siberia_krasnoyarsk_krai_multi"
    },
    {
        "city": "Самарская область",
        "slug": "russia/volga_region_samara_oblast_multi"
    },
    {
        "city": "Республика Башкортостан",
        "slug": "russia/ural_republic_of_bashkortostan_multi"
    },
    {
        "city": "Ростовская область",
        "slug": "russia/volga_region_rostov_oblast_multi"
    },
    {
        "city": "Омская область",
        "slug": "russia/western_siberia_omsk_oblast_multi"
    },
    {
        "city": "Краснодарский край",
        "slug": "russia/southern_russia_krasnodar_krai_multi"
    },
    {
        "city": "Воронежская область",
        "slug": "russia/central_russia_voronezh_oblast_multi"
    },
    {
        "city": "Пермь",
        "slug": "russia/perm"
    },
    {
        "city": "Волгоградская область",
        "slug": "russia/volga_region_volgograd_oblast_multi"
    },
    {
        "city": "Саратовская область",
        "slug": "russia/volga_region_saratov_oblast_multi"
    },
    {
        "city": "Тюменская область",
        "slug": "russia/ural_tyumen_oblast_multi"
    },
    {
        "city": "Самарская область",
        "slug": "russia/volga_region_samara_oblast_multi"
    },
    {
        "city": "Алтайский край",
        "slug": "russia/western_siberia_altai_krai_multi"
    },
    {
        "city": "Республика Удмуртия",
        "slug": "russia/volga_region_udmurt_republic_multi"
    },
    {
        "city": "Республика Дагестан",
        "slug": "russia/southern_russia_republic_of_dagestan_multi"
    },
    {
        "city": "Хабаровский край",
        "slug": "russia/russian_far_east_khabarovsk_krai_multi"
    },
    {
        "city": "Иркутская область",
        "slug": "russia/western_siberia_irkutsk_oblast_multi"
    },
    {
        "city": "Приморский край",
        "slug": "russia/russian_far_east_primorsky_krai_multi"
    },
    {
        "city": "Ярославская область",
        "slug": "russia/golden_ring_yaroslavl_oblast_multi"
    },
    {
        "city": "Кемеровская область",
        "slug": "russia/western_siberia_kemerovo_oblast_multi"
    },
    {
        "city": "Томская область",
        "slug": "russia/western_siberia_tomsk_oblast_multi"
    },
    {
        "city": "Республика Татарстан",
        "slug": "russia/volga_region_republic_of_tatarstan_multi"
    },
    {
        "city": "Севастополь",
        "slug": "russia/sevastopol"
    },
    {
        "city": "Ставропольский край",
        "slug": "russia/southern_russia_stavropol_krai_multi"
    },
    {
        "city": "Оренбургская область",
        "slug": "russia/volga_region_orenburg_oblast_multi"
    },
    {
        "city": "Кемеровская область",
        "slug": "russia/western_siberia_kemerovo_oblast_multi"
    },
    {
        "city": "Рязанская область",
        "slug": "russia/central_russia_ryazan_oblast_multi"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Пензенская область",
        "slug": "russia/volga_region_penza_oblast_multi"
    },
    {
        "city": "Чувашская Республика",
        "slug": "russia/volga_region_chuvash_republic_multi"
    },
    {
        "city": "Липецкая область",
        "slug": "russia/central_russia_lipetsk_oblast_multi"
    },
    {
        "city": "Калининградская область",
        "slug": "russia/northwest_russia_kaliningradskaya_oblast'_province"
    },
    {
        "city": "Астраханская область",
        "slug": "russia/southern_russia_astrakhan_oblast_multi"
    },
    {
        "city": "Тульская область",
        "slug": "russia/central_russia_tula_oblast_multi"
    },
    {
        "city": "Кировская область",
        "slug": "russia/volga_region_kirov_oblast_multi"
    },
    {
        "city": "Краснодарский край",
        "slug": "russia/southern_russia_krasnodar_krai_multi"
    },
    {
        "city": "Курская область",
        "slug": "russia/central_russia_kursk_oblast_multi"
    },
    {
        "city": "Республика Бурятия",
        "slug": "russia/western_siberia_republic_of_buryatia_multi"
    },
    {
        "city": "Тверская область",
        "slug": "russia/central_russia_tver_oblast_multi"
    },
    {
        "city": "Челябинская область",
        "slug": "russia/ural_chelyabinsk_oblast_multi"
    },
    {
        "city": "Сургут",
        "slug": "russia/surgut"
    },
    {
        "city": "Брянская область",
        "slug": "russia/central_russia_bryansk_oblast_multi"
    },
    {
        "city": "Ивановская область",
        "slug": "russia/golden_ring_ivanovo_oblast_multi"
    },
    {
        "city": "Республика Саха",
        "slug": "russia/russian_far_east_sakha_republic_multi"
    },
    {
        "city": "Владимирская область",
        "slug": "russia/golden_ring_vladimir_oblast_multi"
    },
    {
        "city": "Большая Ялта",
        "slug": "russia/big_yalta"
    },
    {
        "city": "Белгородская область",
        "slug": "russia/central_russia_belgorod_oblast_multi"
    },
    {
        "city": "Свердловская область",
        "slug": "russia/ural_sverdlovsk_oblast_multi"
    },
    {
        "city": "Калужская область",
        "slug": "russia/central_russia_kaluga_oblast_multi"
    },
    {
        "city": "Забайкальский край",
        "slug": "russia/western_siberia_zabaykalsky_krai_multi"
    },
    {
        "city": "Чеченская Республика",
        "slug": "russia/southern_russia_chechen_republic_multi"
    },
    {
        "city": "Волгоградская область",
        "slug": "russia/volga_region_volgograd_oblast_multi"
    },
    {
        "city": "Смоленская область",
        "slug": "russia/central_russia_smolensk_oblast_multi"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Республика Мордовия",
        "slug": "russia/volga_region_republic_of_mordovia_multi"
    },
    {
        "city": "Вологодская область",
        "slug": "russia/northwest_russia_vologda_oblast_multi"
    },
    {
        "city": "Курганская область",
        "slug": "russia/ural_kurgan_oblast_province"
    },
    {
        "city": "Вологодская область",
        "slug": "russia/northwest_russia_vologda_oblast_multi"
    },
    {
        "city": "Орловская область",
        "slug": "russia/central_russia_oryol_oblast_multi"
    },
    {
        "city": "Архангельская область",
        "slug": "russia/northwest_russia_arkhangelsk_oblast_province"
    },
    {
        "city": "Республика Северная Осетия",
        "slug": "russia/southern_russia_republic_of_north_ossetia-alania_multi"
    },
    {
        "city": "Нижневартовск",
        "slug": "russia/nizhnevartovsk"
    },
    {
        "city": "Республика Марий Эл",
        "slug": "russia/volga_region_mari_el_republic_multi"
    },
    {
        "city": "Республика Башкортостан",
        "slug": "russia/ural_republic_of_bashkortostan_multi"
    },
    {
        "city": "Мурманская область",
        "slug": "russia/northwest_russia_murmansk_oblast_multi"
    },
    {
        "city": "Костромская область",
        "slug": "russia/golden_ring_kostroma_oblast_multi"
    },
    {
        "city": "Краснодарский край",
        "slug": "russia/southern_russia_krasnodar_krai_multi"
    },
    {
        "city": "Тамбовская область",
        "slug": "russia/central_russia_tambov_oblast_multi"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Республика Кабардино-Балкария",
        "slug": "russia/southern_russia_kabardino-balkar_republic_multi"
    },
    {
        "city": "Ростовская область",
        "slug": "russia/volga_region_rostov_oblast_multi"
    },
    {
        "city": "Республика Татарстан",
        "slug": "russia/volga_region_republic_of_tatarstan_multi"
    },
    {
        "city": "Амурская область",
        "slug": "russia/russian_far_east_amur_oblast_multi"
    },
    {
        "city": "Хабаровский край",
        "slug": "russia/russian_far_east_khabarovsk_krai_multi"
    },
    {
        "city": "Республика Карелия",
        "slug": "russia/northwest_russia_karelia_province"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Ростовская область",
        "slug": "russia/volga_region_rostov_oblast_multi"
    },
    {
        "city": "Саратовская область",
        "slug": "russia/volga_region_saratov_oblast_multi"
    },
    {
        "city": "Новгородская область",
        "slug": "russia/central_russia_novgorod_oblast_multi"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Иркутская область",
        "slug": "russia/western_siberia_irkutsk_oblast_multi"
    },
    {
        "city": "Белгородская область",
        "slug": "russia/central_russia_belgorod_oblast_multi"
    },
    {
        "city": "Иркутская область",
        "slug": "russia/western_siberia_irkutsk_oblast_multi"
    },
    {
        "city": "Республика Коми",
        "slug": "russia/northwest_russia_komi_republic_multi"
    },
    {
        "city": "Нижегородская область",
        "slug": "russia/volga_region_nizhny_novgorod_oblast_multi"
    },
    {
        "city": "Псковская область",
        "slug": "russia/northwest_russia_pskov_oblast_province"
    },
    {
        "city": "Оренбургская область",
        "slug": "russia/volga_region_orenburg_oblast_multi"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Краснодарский край",
        "slug": "russia/southern_russia_krasnodar_krai_multi"
    },
    {
        "city": "Республика Хакасия",
        "slug": "russia/western_siberia_republic_of_khakassia_multi"
    },
    {
        "city": "Саратовская область",
        "slug": "russia/volga_region_saratov_oblast_multi"
    },
    {
        "city": "Алтайский край",
        "slug": "russia/western_siberia_altai_krai_multi"
    },
    {
        "city": "Сахалинская область",
        "slug": "russia/russian_far_east_sakhalin_oblast_multi"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Приморский край",
        "slug": "russia/russian_far_east_primorsky_krai_multi"
    },
    {
        "city": "Кемеровская область",
        "slug": "russia/western_siberia_kemerovo_oblast_multi"
    },
    {
        "city": "Ярославская область",
        "slug": "russia/golden_ring_yaroslavl_oblast_multi"
    },
    {
        "city": "Красноярский край",
        "slug": "russia/western_siberia_krasnoyarsk_krai_multi"
    },
    {
        "city": "Ростовская область",
        "slug": "russia/volga_region_rostov_oblast_multi"
    },
    {
        "city": "Самарская область",
        "slug": "russia/volga_region_samara_oblast_multi"
    },
    {
        "city": "Камчатский край",
        "slug": "russia/russian_far_east_kamchatka_krai_multi"
    },
    {
        "city": "Свердловская область",
        "slug": "russia/ural_sverdlovsk_oblast_multi"
    },
    {
        "city": "Ростовская область",
        "slug": "russia/volga_region_rostov_oblast_multi"
    },
    {
        "city": "Республика Татарстан",
        "slug": "russia/volga_region_republic_of_tatarstan_multi"
    },
    {
        "city": "Челябинская область",
        "slug": "russia/ural_chelyabinsk_oblast_multi"
    },
    {
        "city": "Архангельская область",
        "slug": "russia/northwest_russia_arkhangelsk_oblast_province"
    },
    {
        "city": "Республика Дагестан",
        "slug": "russia/southern_russia_republic_of_dagestan_multi"
    },
    {
        "city": "Большая Ялта",
        "slug": "russia/big_yalta"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Республика Башкортостан",
        "slug": "russia/ural_republic_of_bashkortostan_multi"
    },
    {
        "city": "Челябинская область",
        "slug": "russia/ural_chelyabinsk_oblast_multi"
    },
    {
        "city": "Челябинская область",
        "slug": "russia/ural_chelyabinsk_oblast_multi"
    },
    {
        "city": "Ставропольский край",
        "slug": "russia/southern_russia_stavropol_krai_multi"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Республика Адыгея",
        "slug": "russia/southern_russia_republic_of_adygea_multi"
    },
    {
        "city": "Приморский край",
        "slug": "russia/russian_far_east_primorsky_krai_multi"
    },
    {
        "city": "Пермь",
        "slug": "russia/perm"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Владимирская область",
        "slug": "russia/golden_ring_vladimir_oblast_multi"
    },
    {
        "city": "Республика Башкортостан",
        "slug": "russia/ural_republic_of_bashkortostan_multi"
    },
    {
        "city": "Ставропольский край",
        "slug": "russia/southern_russia_stavropol_krai_multi"
    },
    {
        "city": "Ростовская область",
        "slug": "russia/volga_region_rostov_oblast_multi"
    },
    {
        "city": "Алтайский край",
        "slug": "russia/western_siberia_altai_krai_multi"
    },
    {
        "city": "Калужская область",
        "slug": "russia/central_russia_kaluga_oblast_multi"
    },
    {
        "city": "Республика Тыва",
        "slug": "russia/western_siberia_tuva_republic_multi"
    },
    {
        "city": "Республика Дагестан",
        "slug": "russia/southern_russia_republic_of_dagestan_multi"
    },
    {
        "city": "Нефтеюганск",
        "slug": "russia/nefteyugansk"
    },
    {
        "city": "Республика Ингушетия",
        "slug": "russia/southern_russia_republic_of_ingushetia_multi"
    },
    {
        "city": "Республика Дагестан",
        "slug": "russia/southern_russia_republic_of_dagestan_multi"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Чувашская Республика",
        "slug": "russia/volga_region_chuvash_republic_multi"
    },
    {
        "city": "Тульская область",
        "slug": "russia/central_russia_tula_oblast_multi"
    },
    {
        "city": "Ставропольский край",
        "slug": "russia/southern_russia_stavropol_krai_multi"
    },
    {
        "city": "Ставропольский край",
        "slug": "russia/southern_russia_stavropol_krai_multi"
    },
    {
        "city": "Республика Башкортостан",
        "slug": "russia/ural_republic_of_bashkortostan_multi"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Свердловская область",
        "slug": "russia/ural_sverdlovsk_oblast_multi"
    },
    {
        "city": "Ставропольский край",
        "slug": "russia/southern_russia_stavropol_krai_multi"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Черкесск",
        "slug": "russia/cherkessk"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Ульяновская область",
        "slug": "russia/volga_region_ulyanovsk_oblast_province"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Приморский край",
        "slug": "russia/russian_far_east_primorsky_krai_multi"
    },
    {
        "city": "Волгоградская область",
        "slug": "russia/volga_region_volgograd_oblast_multi"
    },
    {
        "city": "Большая Ялта",
        "slug": "russia/big_yalta"
    },
    {
        "city": "Владимирская область",
        "slug": "russia/golden_ring_vladimir_oblast_multi"
    },
    {
        "city": "Ханты-Мансийск",
        "slug": "russia/khanty-mansiysk"
    },
    {
        "city": "Новый Уренгой",
        "slug": "russia/novy_urengoy"
    },
    {
        "city": "Томская область",
        "slug": "russia/western_siberia_tomsk_oblast_multi"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Нижегородская область",
        "slug": "russia/volga_region_nizhny_novgorod_oblast_multi"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Ростовская область",
        "slug": "russia/volga_region_rostov_oblast_multi"
    },
    {
        "city": "Новосибирская область",
        "slug": "russia/western_siberia_novosibirsk_oblast_multi"
    },
    {
        "city": "Республика Калмыкия",
        "slug": "russia/southern_russia_republic_of_kalmykia_province"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Красноярский край",
        "slug": "russia/western_siberia_krasnoyarsk_krai_multi"
    },
    {
        "city": "Тюменская область",
        "slug": "russia/ural_tyumen_oblast_multi"
    },
    {
        "city": "Ноябрьск",
        "slug": "russia/noyabrsk"
    },
    {
        "city": "Липецкая область",
        "slug": "russia/central_russia_lipetsk_oblast_multi"
    },
    {
        "city": "Республика Татарстан",
        "slug": "russia/volga_region_republic_of_tatarstan_multi"
    },
    {
        "city": "Самарская область",
        "slug": "russia/volga_region_samara_oblast_multi"
    },
    {
        "city": "Республика Удмуртия",
        "slug": "russia/volga_region_udmurt_republic_multi"
    },
    {
        "city": "Курская область",
        "slug": "russia/central_russia_kursk_oblast_multi"
    },
    {
        "city": "Кемеровская область",
        "slug": "russia/western_siberia_kemerovo_oblast_multi"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Ленинградская область",
        "slug": "russia/northwest_russia_leningrad_oblast_province"
    },
    {
        "city": "Свердловская область",
        "slug": "russia/ural_sverdlovsk_oblast_multi"
    },
    {
        "city": "Нижегородская область",
        "slug": "russia/volga_region_nizhny_novgorod_oblast_multi"
    },
    {
        "city": "Кемеровская область",
        "slug": "russia/western_siberia_kemerovo_oblast_multi"
    },
    {
        "city": "Республика Удмуртия",
        "slug": "russia/volga_region_udmurt_republic_multi"
    },
    {
        "city": "Магаданская область",
        "slug": "russia/russian_far_east_magadan_oblast_multi"
    },
    {
        "city": "Тамбовская область",
        "slug": "russia/central_russia_tambov_oblast_multi"
    },
    {
        "city": "Пермь",
        "slug": "russia/perm"
    },
    {
        "city": "Ленинградская область",
        "slug": "russia/northwest_russia_leningrad_oblast_province"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Оренбургская область",
        "slug": "russia/volga_region_orenburg_oblast_multi"
    },
    {
        "city": "Республика Удмуртия",
        "slug": "russia/volga_region_udmurt_republic_multi"
    },
    {
        "city": "Красноярский край",
        "slug": "russia/western_siberia_krasnoyarsk_krai_multi"
    },
    {
        "city": "Псковская область",
        "slug": "russia/northwest_russia_pskov_oblast_province"
    },
    {
        "city": "Ростовская область",
        "slug": "russia/volga_region_rostov_oblast_multi"
    },
    {
        "city": "Белгородская область",
        "slug": "russia/central_russia_belgorod_oblast_multi"
    },
    {
        "city": "Кемеровская область",
        "slug": "russia/western_siberia_kemerovo_oblast_multi"
    },
    {
        "city": "Краснодарский край",
        "slug": "russia/southern_russia_krasnodar_krai_multi"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Красноярский край",
        "slug": "russia/western_siberia_krasnoyarsk_krai_multi"
    },
    {
        "city": "Ростовская область",
        "slug": "russia/volga_region_rostov_oblast_multi"
    },
    {
        "city": "Краснодарский край",
        "slug": "russia/southern_russia_krasnodar_krai_multi"
    },
    {
        "city": "Республика Татарстан",
        "slug": "russia/volga_region_republic_of_tatarstan_multi"
    },
    {
        "city": "Краснодарский край",
        "slug": "russia/southern_russia_krasnodar_krai_multi"
    },
    {
        "city": "Республика Коми",
        "slug": "russia/northwest_russia_komi_republic_multi"
    },
    {
        "city": "Кемеровская область",
        "slug": "russia/western_siberia_kemerovo_oblast_multi"
    },
    {
        "city": "Иркутская область",
        "slug": "russia/western_siberia_irkutsk_oblast_multi"
    },
    {
        "city": "Ленинградская область",
        "slug": "russia/northwest_russia_leningrad_oblast_province"
    },
    {
        "city": "Свердловская область",
        "slug": "russia/ural_sverdlovsk_oblast_multi"
    },
    {
        "city": "Пензенская область",
        "slug": "russia/volga_region_penza_oblast_multi"
    },
    {
        "city": "Нижегородская область",
        "slug": "russia/volga_region_nizhny_novgorod_oblast_multi"
    },
    {
        "city": "Ивановская область",
        "slug": "russia/golden_ring_ivanovo_oblast_multi"
    },
    {
        "city": "Челябинская область",
        "slug": "russia/ural_chelyabinsk_oblast_multi"
    },
    {
        "city": "Оренбургская область",
        "slug": "russia/volga_region_orenburg_oblast_multi"
    },
    {
        "city": "Краснодарский край",
        "slug": "russia/southern_russia_krasnodar_krai_multi"
    },
    {
        "city": "Пермь",
        "slug": "russia/perm"
    },
    {
        "city": "Республика Хакасия",
        "slug": "russia/western_siberia_republic_of_khakassia_multi"
    },
    {
        "city": "Иркутская область",
        "slug": "russia/western_siberia_irkutsk_oblast_multi"
    },
    {
        "city": "Большая Ялта",
        "slug": "russia/big_yalta"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Саратовская область",
        "slug": "russia/volga_region_saratov_oblast_multi"
    },
    {
        "city": "Республика Татарстан",
        "slug": "russia/volga_region_republic_of_tatarstan_multi"
    },
    {
        "city": "Алтайский край",
        "slug": "russia/western_siberia_altai_krai_multi"
    },
    {
        "city": "Ленинградская область",
        "slug": "russia/northwest_russia_leningrad_oblast_province"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Свердловская область",
        "slug": "russia/ural_sverdlovsk_oblast_multi"
    },
    {
        "city": "Московская область и окрестности, Центральный федеральный округ",
        "slug": "russia/central_federal_district_moscow_region_and_vicinity_neighborhood"
    },
    {
        "city": "Ставропольский край",
        "slug": "russia/southern_russia_stavropol_krai_multi"
    },
    {
        "city": "Челябинская область",
        "slug": "russia/ural_chelyabinsk_oblast_multi"
    },
    {
        "city": "Самарская область",
        "slug": "russia/volga_region_samara_oblast_multi"
    },
    {
        "city": "Красноярский край",
        "slug": "russia/western_siberia_krasnoyarsk_krai_multi"
    },
    {
        "city": "Биробиджан",
        "slug": "russia/birobidzhan"
    },
    {
        "city": "Курганская область",
        "slug": "russia/ural_kurgan_oblast_province"
    },
    {
        "city": "Кемеровская область",
        "slug": "russia/western_siberia_kemerovo_oblast_multi"
    }
]

verification_list_citys_slug = []
verification_list_citys = []

index_city = 0

attempt = 0

for city in citys:
    if city["slug"] in verification_list_citys_slug:
        continue

    verification_list_citys_slug.append(city["slug"])

    verification_list_citys.append(city)

print(f"Фильтрация списка городов от дубликатов {len(citys)} => {len(verification_list_citys)}")

citys = verification_list_citys.copy()

files_list = []

for filename in os.listdir("cities"):
    if filename.endswith(".json"):
        with open("cities/" + filename, encoding="utf-8") as json_file:
            data = json.load(json_file)
            files_list.append(data["city"]["slug"])

no_full_hotels_list = []
no_full_index = 0

while index_city < len(citys):
    if no_full_index != index_city:
        no_full_hotels_list = []
        no_full_index = index_city


    if citys[index_city]['slug'] in files_list:
        index_city += 1
        continue

    city = citys[index_city]
    url = f"https://ostrovok.ru/hotel/{city['slug']}/?guests=1&map=true?distance=999&type_group=apart_hotel.hotel.hostel&dates=16.08.2023-22.08.2023"

    if attempt <= 0:
        print(f"Запущен: {index_city + 1} -> {city['city']} -> {city['slug']}")
    else:
        print(f"\t\033[0;33mПопытка {attempt}: {index_city + 1} -> {city['city']} -> {city['slug']}\033[0m")

    data_row = get_ajaxs_url(url)

    if data_row == None:
        if attempt < 30:
            attempt += 1

            #Что за 10 попыток не получен ни один отель
            if attempt > 10 and len(no_full_hotels_list) <= 0:
                print(f"\t\033[0;31mНеудача: за 10 попыток не получен ни один отель\033[0m")
                attempt = 0
                index_city += 1
                continue

            time_sleep = attempt * 0.2 if attempt <= 10 else 2
            sleep(time_sleep)
            continue
        else:
            attempt = 0
            index_city += 1
            print(f"\t\033[0;31mНеудача: за 30 попыток не удалось получить отели\033[0m")

            if len(no_full_hotels_list) <= 0:
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
        with open(f"citys/{index_city}_{city['city']}.json", "w", encoding="utf-8") as file:
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



