from .items import ItemsAPI
from .menu import MenuAPI
from .healthcheck import HealthCheckAPI


def init_routes(api):
    api.add_resource(HealthCheckAPI, '/v1/menu/healthz')
    api.add_resource(ItemsAPI, '/v3/menu/<table_name>')
    api.add_resource(MenuAPI, '/v3/menu')
