from .interpolate import interpolate_subset

__plugins__ = ['recur']

def recur(entries, options_map, config_string=""):
    return interpolate_subset(entries, options_map, {'recur': config_string})
