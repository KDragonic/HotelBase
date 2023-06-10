import argparse
import time


parser = argparse.ArgumentParser()
parser.add_argument('file', type=str, help='Файл логов')
args = parser.parse_args()
path_file = args.file


with open(path_file, "r", encoding='utf-8') as logfile:
    while True:
        data = logfile.read()
        if data:
            print(data, end="")
        time.sleep(0.5)
