import json
import os
import sys

import requests

from requests.auth import HTTPBasicAuth

HOST = os.environ.get('API_HOST')
PROTOCOL = os.environ.get('API_PROTOCOL', 'http')
AUTH = HTTPBasicAuth(os.environ.get('API_USER'), os.environ.get('API_PW'))


def get_data(menu_file) -> dict:
    with open(menu_file) as f:
        menu = json.load(f)
    return menu


def post_item(menu_item):
    url = f'{PROTOCOL}://{HOST}/v1/menu/item'
    r = requests.post(url, json=menu_item, auth=AUTH)
    print(r.status_code)


def delete_item(menu_item):
    url = f'{PROTOCOL}://{HOST}/v1/menu/item'
    r = requests.delete(url, json=menu_item, auth=AUTH)
    print(r.status_code)


if __name__ == '__main__':
    print(__file__)
    menu = get_data('bin/beantown_menu.json')
    sections = menu['categories'].keys()
    for section in sections:
        items = menu['categories'][section]
        for i in items:
            if sys.argv[1] == 'add':
                post_item(i)
            else:
                delete_item(i)
