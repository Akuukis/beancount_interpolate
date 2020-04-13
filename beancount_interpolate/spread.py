from beancount.core.amount import D
from .common import read_config
from .interpolate import interpolate_subset

__plugins__ = ['spread']

def spread(entries, options_map, config_string=""):
    ## Parse config and set defaults
    config_obj = read_config(config_string)
    config = {
      # aliases_before  : config_obj.pop('aliases_before'  , ['spreadBefore']),
        'aliases_after'   : config_obj.pop('aliases_after'   , ['spreadAfter', 'spread']),
        'alias_seperator' : config_obj.pop('seperator    '   , '-'),
        'default_duration': config_obj.pop('default_duration', 'Month'),
        'default_step'    : config_obj.pop('default_step'    , 'Day'),
        'min_value' : D(str(config_obj.pop('min_value'       , 0.05))),
        'max_new_txn'      : config_obj.pop('max_new_txn'      , 9999),
        'suffix'          : config_obj.pop('suffix'          , ' (spread %d/%d)'),
        'tag'             : config_obj.pop('tag'             , 'spreaded'),
        'translations'    : {
            config_obj.pop('account_expenses', 'Expenses'): config_obj.pop('account_assets'  , 'Assets:Current'),
            config_obj.pop('account_income'  , 'Income')  : config_obj.pop('account_liab'    , 'Liabilities:Current'),
        },
    }

    return interpolate_subset(entries, options_map, {'spread': config})
