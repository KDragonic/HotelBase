import os
import json

count = 0

path = ".\cities"

for filename in os.listdir(path):
    if filename.endswith(".json"):
        with open(os.path.join(path, filename)) as json_file:
            data = json.load(json_file)
            count += len(data["hotels"])

print("Количество файлов с объектами на первом уровне: ", count)