from .interpolate import interpolate_subset

__plugins__ = ['depreciate']

def depreciate(entries, options_map, config_string=""):
    return interpolate_subset(entries, options_map, {'depr': config_string})
