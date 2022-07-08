import os
import json
import uuid
from pathlib import Path


path = Path(__file__).resolve().parent


with open(path / "series.json", "r", encoding="utf-8") as f:
    data = json.load(f)

data = list(data)
season = []
episode = [i for i in range(1, 12 + 1)]
pub_year = [i for i in range(1999, 2022 + 1)]
pub_month = [i for i in range(1, 12 + 1)]
finale = [True, False]

file_list = os.listdir(path)


data[0]["series"]["uuid"] = "8e2e8571-de49-4551-a525-39f7cb0b672e"
data[0]["series"]["name"] = "月光下的異世界之旅"
data[0]["series"]["season"] = "秋"
data[0]["series"]["episodes"] = 12
data[0]["series"]["pub_year"] = "2020"
data[0]["series"]["pub_month"] = "11"
data[0]["series"]["finale"] = True

data[0]["videos"][0]["uuid"] = "2eb5de06-4765-4f67-be9d-f3db38e2111d"
data[0]["videos"][0]["episode"] = "1"
data[0]["videos"][0]["path"] = str(path / "[Tsuki ga Michibiku Isekai Douchuu][01][1080P].mp4")

data[0]["videos"][1]["uuid"] = "a3652994-b607-4a99-8ac2-ed0fcc683a76"
data[0]["videos"][1]["episode"] = "2"
data[0]["videos"][1]["path"] = str(path / "[Tsuki ga Michibiku Isekai Douchuu][02][1080P].mp4")

with open(path / "series.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
