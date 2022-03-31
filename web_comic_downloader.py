"""Take list of comics from main_page_update_comics.csv and use the URLs + CSS selectors to grab images and save them to a file on my desktop

Functions:
    basic_image_dl(str, str)
TODO separate_page_dl (might just be an optional function called in basic_image_dl)

TODO:
Gunnerkrigg will mess it up, could make it intelligently construct the comic_url based on info given and depending on what it sees in the src
https://www.gunnerkrigg.com/,.comic_image
Haven't yet gone through the ones that need me to click into another page - each will have to be individually coded, I think - just with requests/bs4 is fine, I think
Ah, I could just use a flag or optional argument that might direct it to navigate to another page - should probably define it as another function
I would keep all the data in one csv file, then.
Look into doing it for manga/reddit or via RES
"""
import csv
import logging
import re
from pathlib import Path

import bs4
import requests

logging.basicConfig(
    filename="generic_DEBUG.txt",
    level=logging.DEBUG,
    format=" %(asctime)s - %(levelname)s - %(message)s",
)
logging.disable(logging.CRITICAL)


def basic_image_dl(url: str, css_selector: str):
    """Take a URL and download the most recent image if it doesn't exist already"""
    print(f"Accessing {url}...")
    res = requests.get(f"{url}")
    res.raise_for_status()
    # could navigate to another page here, if necessary
    soup = bs4.BeautifulSoup(res.text, "lxml")

    image_elements = soup.select(css_selector)
    if image_elements == []:
        print("Could not find comic image.")
        return None
    image_url = image_elements[0].get("src")
    site_name = site_name_from_url.match(image_url).group(1)
    folder_path = Path(f"webcomics/{site_name}")
    folder_path.mkdir(parents=True, exist_ok=True)
    image_path = folder_path / Path(image_url).name

    if image_path.exists():
        print("No new updates...")
        return None

    print(f"Downloading image {image_url}...")
    res = requests.get(image_url)
    res.raise_for_status()
    with image_path.open("wb") as image:
        for chunk in res.iter_content(100000):
            image.write(chunk)


if __name__ == "__main__":
    site_name_from_url = re.compile(r"https://(?:www.)?(\w*)\.")
    with open("main_page_update_comics.csv", "r") as comic_list:
        reader_obj = csv.reader(comic_list)
        for row in reader_obj:
            basic_image_dl(row[0], row[1])
