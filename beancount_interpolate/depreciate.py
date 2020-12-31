from beancount.core.amount import D
from .common import read_config
from .interpolate import interpolate_subset

__plugins__ = ['depreciate']

def depreciate(entries, options_map, config_string=""):
    ## Parse config and set defaults
    config_obj = read_config(config_string)
    config = {
      # aliases_before  : config_obj.pop('aliases_before'  , ['spreadBefore']),
        'aliases_after'   : config_obj.pop('aliases_after'   , ['deprAfter', 'depr']),
        'alias_seperator' : config_obj.pop('seperator    '   , '-'),
        'default_duration': config_obj.pop('default_duration', 'Year'),
        'default_step'    : config_obj.pop('default_step'    , 'Day'),
        'min_value' : D(str(config_obj.pop('min_value'       , 0.05))),
        'max_new_tx'      : config_obj.pop('max_new_tx'      , 9999),
        'suffix'          : config_obj.pop('suffix'          , ' (depr %d/%d)'),
        'tag'             : config_obj.pop('tag'             , 'depreciated'),
        'translations'    : {
            config_obj.pop('account_assets'  , 'Assets:Fixed')     : config_obj.pop('account_expenses', 'Expenses:Depreciation'),
            config_obj.pop('account_liab'    , 'Liabilities:Fixed'): config_obj.pop('account_income'  , 'Income:Appreciation'),
        },
    }

    return interpolate_subset(entries, options_map, {'depr': config})
