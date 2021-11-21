import json
import os
import sys

import requests

from requests.auth import HTTPBasicAuth

HOST = os.environ.get('MENU_API_HOST')
AUTH = HTTPBasicAuth(os.environ.get('API_USERNAME'), os.environ.get('API_PASSWORD'))
PROTOCOL = os.environ.get('MENU_API_PROTOCOL')
HEADERS = {
    "Content-Type": "application/json"
}


def get_data(menu_file) -> dict:
    with open(menu_file) as f:
        menu = json.load(f)
    return menu


def get_item(slug):
    url = f"{PROTOCOL}://{HOST}/v1/menu/{slug}"
    r = requests.get(url, auth=AUTH, headers=HEADERS)
    print(f"Item {slug} status {r.status_code}")
    return r.status_code


def post_item(menu_item):
    url = f"{PROTOCOL}://{HOST}/v1/menu/{menu_item['name']}"
    r = requests.post(url, json=menu_item, auth=AUTH)
    print(r.status_code)


def put_item(menu_item):
    url = f"{PROTOCOL}://{HOST}/v1/menu/{menu_item['slug']}"
    r = requests.put(url, json=menu_item, auth=AUTH)
    print(r.status_code)


def delete_item(menu_item):
    url = f"{PROTOCOL}://{HOST}/v1/menu/{menu_item['name']}"
    r = requests.delete(url, auth=AUTH)
    print(r.status_code)


def create_food_items(menu):
    sections = menu['categories'].keys()
    for section in sections:
        items = menu['categories'][section]
        for i in items:
            if i.get('location'):
                del i['location']
            if sys.argv[1] == 'add':
                if not i.get('slug'):
                    i['slug'] = i['name'].lower().replace(' ', '-')
                status = get_item(i['slug'])
                if status == 200:
                    print(f"UPDATING item {i['name']}")
                    put_item(i)
                else:
                    print(f"CREATING item {i['name']}")
                    post_item(i)
            else:
                delete_item(i)

def create_categories(menu):
    categories = menu['categories'].keys()
    for category in categories:
        data = {
            "name": category,
            "is_active": True
        }
        url = f"{PROTOCOL}://{HOST}/v1/categories/{category}"
        r = requests.post(url, json=data, auth=AUTH)
        print(f"Status: {r.status_code}")


if __name__ == '__main__':
    print(__file__)
    menu = get_data('bin/beantown_menu.json')
    create_categories(menu)
    create_food_items(menu)
