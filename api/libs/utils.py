import uuid


def get_uuid():
    return str(uuid.uuid4())


def convert_to_bool(value):
    if not isinstance(value, bool):
        if value == 'true':
            value = True
        elif value == 'false':
            value = False
    return value


def make_slug(name):
    slug = name.lower().replace(' ', '-').replace('.', '').strip('*')
    return slug


class ParamArgs:
    def __init__(self, args):
        self.is_active = args.get('is_active')
        self.location = args.get('location')
        self.name = args.get('name')
        self.sku = args.get('sku')
        self.status = self._convert_to_bool(self.is_active)

    def __repr__(self):
        return f'Location: {self.location} | SKU: {self.sku} | Product: {self.name}'

    def to_dict(self):
        args_dict = {
            "status": self.status,
            "location": self.location,
            "sku": self.sku,
            "name": self.name
        }
        return args_dict

    def _convert_to_bool(self, value):
        if not isinstance(value, bool):
            if value == 'true':
                value = True
            elif value == 'false':
                value = False
        return value
