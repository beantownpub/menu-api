from .menu_items import MenuItemsAPI, MenuItemAPI, SectionsAPI, DrinksAPI
from .catering_menu import CateringAPI


def init_routes(api):
    api.add_resource(MenuItemsAPI, '/v1/menu/items')
    api.add_resource(MenuItemAPI, '/v1/menu/item/<item>')
    api.add_resource(SectionsAPI, '/v1/menu/section/<category>')
    api.add_resource(DrinksAPI, '/v1/menu/drinks/<category>')
    api.add_resource(CateringAPI, '/v1/menu/catering')
