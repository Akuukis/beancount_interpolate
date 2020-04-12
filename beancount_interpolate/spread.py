from .interpolate import interpolate_subset

__plugins__ = ['spread']

def spread(entries, options_map, config_string=""):
    return interpolate_subset(entries, options_map, {'spread': config_string})
