
def convert_to_bool(value):
    if not isinstance(value, bool):
        if value == 'true':
            value = True
        elif value == 'false':
            value = False
    return value
