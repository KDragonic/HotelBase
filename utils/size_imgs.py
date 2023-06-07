import json
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Список ссылок на фото
photo_urls = []

hotel_has_room = []
hotel_count_img = []
hotel_count = 0

def convert_bytes(num):
    """
    Эта функция преобразует количество байт в соответствующие единицы измерения в зависимости от размера файла
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            if x == 'MB':
                return f"{num:.1f} {x}"
            else:
                return f"{num:.0f} {x}"
        num /= 1024.0

path = "./hotels"

for filename in os.listdir(path):
    if filename.endswith(".json"):
        with open(os.path.join(path, filename), encoding='utf-8') as json_file:
            data = json.load(json_file)
            hotel_count += 1
            count_img = 0
            if len(data["rooms"]) > 0:
              hotel_has_room.append(filename)
              for room in data["rooms"]:
                count_img += len(room["imgs"])
                [photo_urls.append(img["url"]) for img in room["imgs"]]

            if len(data["images"]) > 0:
              count_img += len(data["images"])
              [photo_urls.append(img["url"]) for img in data["images"]]

            if count_img > 0:
              hotel_count_img.append(count_img)

print(f"Минимум [{min(hotel_count_img)}], среднее [{round(sum(hotel_count_img) / len(hotel_count_img))}], максимум фоток [{max(hotel_count_img)}]")
print("hotel_has_room", len(hotel_has_room))
print("hotel_count", hotel_count)
print("photo_urls", len(photo_urls))

# Параллельно обрабатываем все ссылки
def get_photo_size(url):
    if len(url) <= 2:
      url = url[1]
    try:
      response = requests.head(url)
      if response.status_code == 200:
          return int(response.headers.get("content-length", 0))
      return 0
    except:
      return 0

total_size = 0

import multiprocessing
max_workers = multiprocessing.cpu_count()

with ThreadPoolExecutor(max_workers=max_workers*3) as executor:
    futures = [executor.submit(get_photo_size, url) for url in enumerate(photo_urls)]
    len_futures = len(futures)
    for i, future in enumerate(as_completed(futures)):
        total_size += future.result()
        print(f"[{i+1}/{len_futures}]. Размер всех фото: {convert_bytes(total_size)}\t\t\t", end='\r')


print(f"[{len_futures}/{len_futures}]. Размер всех фото: {convert_bytes(total_size)}\t\t\t")
