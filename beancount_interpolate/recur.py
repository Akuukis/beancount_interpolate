from beancount.core.amount import D
from .common import read_config
from .interpolate import interpolate_subset

__plugins__ = ['recur']

def recur(entries, options_map, config_string=""):
    config_obj = read_config(config_string)
    config = {
        # ALIASES_BEFORE  : config_obj.pop('aliases_before'  , ['recurBefore']),
        'aliases_after'   : config_obj.pop('aliases_after'   , ['recurAfter', 'recur']),
        'alias_seperator' : config_obj.pop('aliases_after'   , '-'),
        'default_duration': config_obj.pop('default_duration', 'inf'),
        'default_step'    : config_obj.pop('default_step'    , 'Day'),
        'min_value' : D(str(config_obj.pop('min_value'       , 0.05))),
        'max_new_txn'      : config_obj.pop('max_new_txn'      , 9999),
        'suffix'          : config_obj.pop('suffix'          , ' (recur %d/%d)'),
        'tag'             : config_obj.pop('tag'             , 'recurred'),
    }
    return interpolate_subset(entries, options_map, {'recur': config})
