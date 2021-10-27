import os
from datetime import datetime, timedelta
from pprint import pprint
from urllib.parse import urlsplit

import requests
from dotenv import load_dotenv


def download_pictures(links: list, name: str) -> None:
    img_path = f'images/{name}'
    if not os.path.exists(img_path):
        try:
            os.makedirs(img_path)
        except FileExistsError as ex:
            print(ex)

    for index, link in enumerate(links, start=1):
        resp = requests.get(link)
        resp.raise_for_status()
        ext = _get_file_extension(link)
        with open(f'{img_path}/{index}_{name}{ext}', 'wb') as f:
            f.write(resp.content)


def get_all_launches_id() -> list:
    url = f'https://api.spacexdata.com/v5/launches/'
    resp = requests.get(url)
    resp.raise_for_status()
    return [lounch['id'] for lounch in resp.json()]


def get_last_launch_img_links(launches_id: list) -> list:
    url_launches = f'https://api.spacexdata.com/v5/launches/'
    last_launch_with_imgs = {}
    counter = 1
    print(counter)
    for id in reversed(launches_id):
        url = f'{url_launches}{id}'
        resp = requests.get(url).json()
        launch_imgs = resp['links']['flickr'].get('original')
        if launch_imgs:
            last_launch_with_imgs = {
                'flight_number': resp.get('flight_number'),
                'id': id,
                'links': launch_imgs
            }
            break
        counter += 1
        print(counter)
    return last_launch_with_imgs.get('links')


def fetch_spacex_last_launch() -> None:
    launches_id = get_all_launches_id()
    last_launch_with_img = get_last_launch_img_links(launches_id)
    download_pictures(last_launch_with_img, 'spacex')


def _get_file_extension(url: str) -> str:
    path = urlsplit(url).path
    return os.path.splitext(path)[1]


def get_apod_img_links(days: int) -> None:
    load_dotenv()
    url = 'https://api.nasa.gov/planetary/apod'
    options = {
        'api_key': os.environ.get('NASA_API_KEY'),
        'start_date': (datetime.now() - timedelta(days)).strftime('%Y-%m-%d'),
        'end_date': datetime.now().strftime('%Y-%m-%d'),
    }
    resp = requests.get(url, params=options)
    resp.raise_for_status()
    links = []
    for day in resp.json():
        if day.get('media_type') == 'image':
            url = day.get('url')
            if url:
                links.append(url)
    return links


def fetch_nasa_apods(days) -> None:
    links = get_apod_img_links(days)
    download_pictures(links, 'nasa')


def get_nasa_epic_img_links(days: int) -> list:
    load_dotenv()
    url_info = 'https://api.nasa.gov/EPIC/api/natural/all'
    options = {
        'api_key': os.environ.get('NASA_API_KEY')
    }
    resp = requests.get(url_info, params=options)
    resp.raise_for_status()

    key = options.get('api_key')
    links = []
    for day in resp.json()[:days]:
        date = day.get('date').replace('-', '/').split()[0]
        image = day.get('image')
        url_img = f'https://api.nasa.gov/EPIC/archive/natural/{date}/png/{image}.png?api_key={key}'
        links.append(url_img)
    return links


def fetch_nasa_epic_imgs(days):
    links = get_nasa_epic_img_links(days)
    # download_pictures(links, 'nasa_epic')
    pprint(links)
    print(len(links))


if __name__ == '__main__':
    # fetch_spacex_last_launch()
    # print(get_file_extension('https://example.com/txt/hello%20world.txt?v=9#python'))
    # res = get_apod(30)
    # pprint(res)
    # fetch_nasa_apods(10)
    fetch_nasa_epic_imgs(5)
