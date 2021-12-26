from .food import FoodAPI, FoodItemsAPI, ItemsByCategoryAPI
from .categories import CategoryAPI, CategoriesAPI
from .healthcheck import HealthCheckAPI
from .sides import SidesAPI

categories_api_routes = [
    '/v1/categories',
    '/v2/menu/categories'
]

category_api_routes = [
    '/v1/categories/<name>',
    '/v2/menu/categories/<name>'
]

items_by_category_routes = [
    '/v2/menu/items'
]

food_api_routes = [
    '/v2/menu/items/<name>',
    '/v1/menu/<name>'
]

food_items_api_routes = [
    '/v1/menu/items',
    '/v2/menu/items'
]

def init_routes(api):
    api.add_resource(FoodItemsAPI, *food_items_api_routes)
    api.add_resource(ItemsByCategoryAPI, *items_by_category_routes)
    api.add_resource(FoodAPI, *food_api_routes)
    api.add_resource(CategoryAPI, *category_api_routes)
    api.add_resource(CategoriesAPI, *categories_api_routes)
    api.add_resource(HealthCheckAPI, '/v2/menu/healthz')
    api.add_resource(SidesAPI, '/v2/menu/sides')
