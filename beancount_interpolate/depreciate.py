__author__ = 'Akuukis <akuukis@kalvis.lv>'

from beancount.core.number import D
from beancount.core.data import filter_txns

from .common import extract_mark_tx
from .common import extract_mark_posting
from .common import new_filtered_entries
from .common import distribute_over_period
from .common import read_config

__plugins__ = ['depreciate']


def depreciate(entries, options_map, config_string=""):
    """
    Beancount plugin: Generates new entries to depreciate target posting over given period.

    Args:
      entries: A list of directives. We're interested only in the Transaction instances.
      options_map: A parser options dict.
      config_string: A configuration string in JSON format given in source file.
    Returns:
      A tuple of entries and errors.
    """

    errors = []

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

    newEntries = []
    for tx in filter_txns(entries):

        # Spread at posting level because not all account types may be eligible.
        selected_postings = []
        for i, posting in enumerate(tx.postings):
            # We are interested in only marked postings. TODO: ALIASES_BEFORE.
            params = extract_mark_posting(posting, config) \
                  or extract_mark_tx(tx, config) \
                  or False
            if not params:
                continue

            for translation in config['translations']:
                if posting.account[0:len(translation)] == translation:
                    new_account = config['translations'][translation] + posting.account[len(translation):]
                    selected_postings.append( (i, new_account, params, posting) )

        # For selected postings no need to change the original.
        pass

        # For selected postings add new postings bundled into entries.
        if len(selected_postings) > 0:
            newEntries = newEntries + new_filtered_entries(tx, params, distribute_over_period, selected_postings, config)

    return entries + newEntries, errors
