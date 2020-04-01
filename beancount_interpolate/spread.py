__author__ = 'Akuukis <akuukis@kalvis.lv'

from beancount.core.amount import Amount
from beancount.core.data import filter_txns
from beancount.core.data import Posting
from beancount.core.number import D

from .parser import find_marked
from .common import extract_mark_tx
from .common import extract_mark_posting
from .common import parse_mark
from .common import new_filtered_entries
from .common import distribute_over_period
from .common import read_config

__plugins__ = ['spread']


def distribute_over_period_negative(period, total_value, config):
    return distribute_over_period(period, -total_value, config)


def spread(entries, options_map, config_string=""):
    """
    Beancount plugin: Generate new entries to allocate P&L of target income/expense posting over given period.

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
        'aliases_after'   : config_obj.pop('aliases_after'   , ['spreadAfter', 'spread']),
        'alias_seperator' : config_obj.pop('seperator    '   , '-'),
        'default_duration': config_obj.pop('default_duration', 'Month'),
        'default_step'    : config_obj.pop('default_step'    , 'Day'),
        'min_value' : D(str(config_obj.pop('min_value'       , 0.05))),
        'max_new_tx'      : config_obj.pop('max_new_tx'      , 9999),
        'suffix'          : config_obj.pop('suffix'          , ' (spread %d/%d)'),
        'tag'             : config_obj.pop('tag'             , 'spreaded'),
        'translations'    : {
            config_obj.pop('account_expenses', 'Expenses'): config_obj.pop('account_assets'  , 'Assets:Current'),
            config_obj.pop('account_income'  , 'Income')  : config_obj.pop('account_liab'    , 'Liabilities:Current'),
        },
    }

    newEntries = []

    unmarked_entries, marked_entries = find_marked(entries, config)

    for tx, period in marked_entries:

        # Spread at posting level because not all account types may be eligible.
        selected_postings = []
        for i, posting in enumerate(tx.postings):
            for translation in config['translations']:
                if posting.account[0:len(translation)] == translation:
                    new_account = config['translations'][translation] + posting.account[len(translation):]
                    selected_postings.append((i, new_account, posting))

        # For selected postings change the original.
        for i, new_account, posting in selected_postings:
            tx.postings.pop(i)
            tx.postings.insert(i, Posting(
                account=new_account,
                units=Amount(posting.units.number, posting.units.currency),
                cost=None,
                price=None,
                flag=None,
                meta=None))

        # For selected postings add new postings bundled into entries.
        if len(selected_postings) > 0:
            newEntries = newEntries + new_filtered_entries(tx, period, distribute_over_period_negative, selected_postings, config)

    return unmarked_entries + marked_entries + newEntries, errors
