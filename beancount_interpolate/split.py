from .interpolate import interpolate_subset

__plugins__ = ['split']

def split(entries, options_map, config_string=""):
    return interpolate_subset(entries, options_map, {'split': config_string})
