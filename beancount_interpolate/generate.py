from beancount.core.amount import Amount
from beancount.core.data import filter_txns
from beancount.core.number import D

from .common import extract_mark_tx
from .common import new_whole_entries
from .common import read_config

__plugins__ = ['generate']


def duplicate_over_period(period, value, config):
    amounts = []
    for i in range(period):
        amounts.append( D(str(value)) )

    return amounts


def recur(entries, options_map, config_string):
    """
    Beancount plugin: Dublicates all entry postings over time.

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
        # ALIASES_BEFORE  : config_obj.pop('aliases_before'  , ['recurBefore']),
        'aliases_after'   : config_obj.pop('aliases_after'   , ['recurAfter', 'recur']),
        'alias_seperator' : config_obj.pop('aliases_after'   , '-'),
        'default_duration': config_obj.pop('default_duration', 'inf'),
        'default_step'    : config_obj.pop('default_step'    , 'Day'),
        'min_value' : D(str(config_obj.pop('min_value'       , 0.05))),
        'max_new_tx'      : config_obj.pop('max_new_tx'      , 9999),
        'suffix'          : config_obj.pop('suffix'          , ' (recur %d/%d)'),
        'tag'             : config_obj.pop('tag'             , 'recurred'),
    }

    newEntries = []
    trashbin = []
    for tx in filter_txns(entries):

        # Recur at entry level only, so that it balances.
        pass

        # We are interested in only marked entries. TODO: ALIASES_BEFORE.
        params = extract_mark_tx(tx, config)
        if not params:
            continue

        # For selected entries add new entries.
        trashbin.append(tx)
        newEntries = newEntries + new_whole_entries(tx, params, dublicate_over_period, config)

    for trash in trashbin:
        entries.remove(trash)

    return entries + newEntries, errors
