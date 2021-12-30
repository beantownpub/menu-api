import uuid


def make_uuid():
    return str(uuid.uuid4())


def convert_to_bool(value):
    if not isinstance(value, bool):
        if value == 'true':
            value = True
        elif value == 'false':
            value = False
    return value


def make_slug(name):
    slug = name.lower().replace(' ', '-').replace('.', '').replace('&', 'and').strip('*')
    return slug


def convert_to_dict(item):
    item_dict = item.__dict__
    if item_dict.get('_sa_instance_state'):
        del item_dict['_sa_instance_state']
    if item_dict.get('creation_date'):
        del item_dict['creation_date']
    return item_dict

class ParamArgs:
    def __init__(self, args):
        self.active_only = args.get('active_only')
        self.args = args
        self.category = args.get('category')
        self.inactive_only = args.get('inactive_only')
        self.is_active = args.get('is_active')
        self.location = args.get('location')
        self.name = args.get('name')
        self.sku = args.get('sku')
        self.status = self.get_status()
        self.with_items = self._convert_to_bool(args.get('with_items'))

    def __repr__(self):
        return repr(self.map)

    @property
    def map(self):
        args_dict = {
            "location": self.location,
            "name": self.name,
            "sku": self.sku,
            "status": self.status,
            "with_items": self.with_items
        }
        return args_dict

    def get_status(self):
        if not self.args.get('status'):
            status = self._convert_to_bool(self.is_active)
        else:
            status = self.args.get('status')
        return status

    def _convert_to_bool(self, value):
        if not isinstance(value, bool):
            if value == 'true':
                value = True
            elif value == 'false':
                value = False
        return value
