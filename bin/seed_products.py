import argparse
import json
import os
import sys

import requests

from requests.auth import HTTPBasicAuth

class SeedMenuException(Exception):
    """Base class for seeding menu exceptions"""


USER = os.environ.get('API_USERNAME')
PWD = os.environ.get('API_PASSWORD')
AUTH = HTTPBasicAuth(username=os.environ.get('API_USERNAME'), password=os.environ.get('API_PASSWORD'))
HEADERS = {
    "Content-Type": "application/json"
}


def parse_args():
    env = {"help": "The environment to seed", "type": str, "required": True}
    location = {"help": "The location to seed", "type": str, "required": True}
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--env", **env)
    parser.add_argument("-l", "--location", **location)
    return parser.parse_args()

class FoodMenu():
    def __init__(self, env, location):
        self.env = env
        self.location = location
        self.url = self._get_url()
        self.data = self._get_data()
        self.categories = self.data['categories'].keys()
        self.sides = self.data['sides']

    def _get_url(self):
        if self.env == 'dev':
            url = os.environ.get('DEV_MENU_API_URL')
        elif args.env == 'prod':
            url = os.environ.get('PROD_MENU_API_URL')
        else:
            raise SeedMenuException("Invalid env")
        return url

    def _get_data(self):
        menu_file = f'bin/data/{self.location}.json'
        with open(menu_file) as f:
            menu = json.load(f)
        return menu

    def _get_category_data(self, category):
        data = self.data['categories'][category].copy()
        return data

    def get_item_by_slug(self, item_type, slug):
        url = f"{self.url}/v2/menu/{item_type}/{slug}?location={self.location}"
        r = requests.get(url, auth=AUTH, headers=HEADERS)
        print(f'STATUS: {item_type} {slug} {r.status_code}')
        return r.status_code

    def get_category_by_slug(self, item_type, slug):
        url = f"{self.url}/v2/menu/{item_type}/{slug}?location={self.location}"
        r = requests.get(url, auth=AUTH, headers=HEADERS)
        if r.status_code != 200 or r.status_code != 404:
            print(f'STATUS: {item_type} {slug} {r.status_code}')
        return r.status_code

    def post_item(self, item_type, data):
        if item_type == 'items':
            url = f"{self.url}/v1/menu/{item_type}?location={self.location}"
        else:
            url = f"{self.url}/v2/menu/{item_type}?location={self.location}"
        r = requests.post(url, json=data, auth=AUTH)
        print(f"Create {data['name']} status {r.status_code}")
        if r.status_code != 201:
            raise SeedMenuException('Invalid Status %s | %s', r.status_code, r.content)

    def make_slug(self, name):
        slug = name.lower().replace(' ', '-').strip('*')
        return slug

    def create_food_items(self):
        for category in self.categories:
            items = self.data['categories'][category]['items']
            for i in items:
                if not i.get('slug'):
                    i['slug'] = self.make_slug(i['name'])
                status = self.get_item_by_slug('items', i['slug'])
                if status != 200:
                    print(f"Creating item {i['name']}\n{i}")
                    self.post_item('items', i)

    def create_categories(self):
        for category in self.categories:
            data = self._get_category_data(category)
            data['name'] = category
            if data.get('items'):
                del data['items']
            if not data.get('slug'):
                data['slug'] = self.make_slug(category)
            status = self.get_item_by_slug('categories', data['slug'])
            if status == 200:
                print(f"Category {category} already exists")
            else:
                self.post_item('categories', data)

    def create_sides(self):
        for side in self.sides:
            data = {
                "name": side,
                "price": 0.0,
                "location": self.location,
                "is_active": True
            }
            self.post_item('sides', data)


def put_item(url, menu_item, location):
    slug = menu_item['name'].lower().replace(' ', '-')
    url = f"{url}/v1/menu/{slug}?location={location}"
    r = requests.put(url, json=menu_item, auth=AUTH)
    print(f"Update {menu_item['name']} status {r.status_code}")


def put_category(url, menu_item, location):
    slug = menu_item['name'].lower().replace(' ', '-')
    url = f"{url}/v1/categories/{slug}?location={location}"
    r = requests.put(url, json=menu_item, auth=AUTH)
    print(f"Update {menu_item['name']} status {r.status_code}")


def delete_item(url, menu_item, location):
    slug = menu_item['name'].lower().replace(' ', '-')
    url = f"{url}/v1/menu/{slug}?location={location}"
    r = requests.delete(url, auth=AUTH)
    print(f"Delete {menu_item['name']} status {r.status_code}")


if __name__ == '__main__':
    print(__file__)
    args = parse_args()
    menu = FoodMenu(args.env, args.location)
    menu.create_categories()
    menu.create_food_items()
    menu.create_sides()
