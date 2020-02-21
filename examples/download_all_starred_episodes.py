import pocketcasts as pc
import requests
import re
import configparser
from pathlib import Path


def get_valid_filename(s):
    s = str(s).strip()
    return re.sub(r"(?u)[^-\w. ]", "", s)


print("Reading configuration file config.ini.")

config = configparser.ConfigParser()
config.read("config.ini")

print("Connecting to Pocketcasts API.")
api = pc.Api(config["pocketcasts"]["user"], config["pocketcasts"]["password"])

print("Fetching all starred episodes.")
starred = api.starred_episodes()

print("Downloading starred episodes.")
total_size = len(starred)

Path("podcasts/").mkdir(parents=True, exist_ok=True)
for index, i in enumerate(starred, 1):
    filename = get_valid_filename(
        f"{i._published_at.strftime('%Y%m%d')} - {i._podcast._title} - {i._title}.{i._url.split('.')[-1]}"
    )
    print(f"Downloading {index}/{total_size} : {filename}")
    r = requests.get(i._url)
    with open("podcasts/" + filename, "wb") as f:
        f.write(r.content)
