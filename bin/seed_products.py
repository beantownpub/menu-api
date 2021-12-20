import json
import os
import sys

import requests

from requests.auth import HTTPBasicAuth

HOST = os.environ.get('MENU_API_HOST')
USER = os.environ.get('API_USERNAME')
PWD = os.environ.get('API_PASSWORD')
AUTH = HTTPBasicAuth(username=os.environ.get('API_USERNAME'), password=os.environ.get('API_PASSWORD'))
PROTOCOL = os.environ.get('MENU_API_PROTOCOL')
HEADERS = {
    "Content-Type": "application/json"
}
UPDATE = False


def get_data(menu_file) -> dict:
    with open(menu_file) as f:
        menu = json.load(f)
    return menu


def get_item(item, item_type):
    slug = item['name'].lower().replace(' ', '-')
    url = f"{PROTOCOL}://{HOST}/v1/menu/{item_type}/{slug}?location=beantown"
    r = requests.get(url, auth=AUTH, headers=HEADERS)
    return r.status_code


def post_item(menu_item):
    url = f"{PROTOCOL}://{HOST}/v1/menu/items?location=beantown"
    r = requests.post(url, json=menu_item, auth=AUTH)
    print(f"Create {menu_item['name']} status {r.status_code}")


def put_item(menu_item):
    slug = menu_item['name'].lower().replace(' ', '-')
    url = f"{PROTOCOL}://{HOST}/v1/menu/{slug}?location=beantown"
    r = requests.put(url, json=menu_item, auth=AUTH)
    print(f"Update {menu_item['name']} status {r.status_code}")


def delete_item(menu_item):
    slug = menu_item['name'].lower().replace(' ', '-')
    url = f"{PROTOCOL}://{HOST}/v1/menu/{slug}?location=beantown"
    r = requests.delete(url, auth=AUTH)
    print(f"Delete {menu_item['name']} status {r.status_code}")


def create_food_items(menu):
    sections = menu['categories'].keys()
    for section in sections:
        items = menu['categories'][section]['items']
        for i in items:
            if sys.argv[1] == 'add':
                status = get_item(i, 'items')
                if status == 200:
                    if not UPDATE:
                        print(f"Item {i['name']} already exists")
                    else:
                        print(f"Updating item {i['name']}")
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
            "is_active": menu['categories'][category]['is_active'],
            "description": menu['categories'][category]['description'],
            "location": menu['categories'][category]['location']
        }
        url = f"{PROTOCOL}://{HOST}/v2/menu/categories?location=beantown"
        status = get_item(data, 'categories')
        print(f"Status {category}: {status}")
        if status != 200:
            r = requests.post(url, json=data, auth=AUTH)
            print(f"Create {category}: {r.status_code}")


if __name__ == '__main__':
    print(__file__)
    menu = get_data('bin/data/beantown_menu.json')
    create_categories(menu)
    create_food_items(menu)
