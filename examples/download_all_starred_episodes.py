import pocketcasts as pc
import requests
import re
import configparser
from pathlib import Path


def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = str(s).strip().replace(" ", "_")
    return re.sub(r"(?u)[^-\w.]", "", s)


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
for index, i in enumerate(starred):
    filename = get_valid_filename(
        f"{i._published_at.split('_')[-1]} - {i._podcast._title} - {i._title}.{i._url.split('.')[-1]}"
    )
    print(f"{index}/{total_size} : {filename}")
    r = requests.get(i._url)
    with open("podcasts/" + filename, "wb") as f:
        f.write(r.content)
