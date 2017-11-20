import json

config_keys = json.load(open('config.json', 'r'))


class Data:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class ConfigException(Exception):
    pass


def read(keys):
    full_dat = {}
    for key in keys:
        val = keys[key]
        if type(val) == dict:
            full_dat[key] = Data(**read(val))
        else:
            full_dat[key] = val
    return full_dat


conf_keys = read(config_keys)

for key in conf_keys:
    val = conf_keys[key]
    if key not in globals():
        globals()[key] = val
    else:
        raise ConfigException, 'Key overlaps either a builtin var, or another config'
