__author__ = 'Akuukis <akuukis@kalvis.lv'

from beancount.core.amount import Amount
from beancount.core.data import filter_txns
from beancount.core.number import D

from .common import extract_mark_entry
from .common import distribute_over_period
from .common import new_whole_entries

__plugins__ = ['split']


def split(entries, options_map, config_string):
    """
    Beancount plugin: Dublicates all entry postings over time at fraction of value.

    Args:
      entries: A list of directives. We're interested only in the Transaction instances.
      options_map: A parser options dict.
      config_string: A configuration string in JSON format given in source file.
    Returns:
      A tuple of entries and errors.
    """

    errors = []

    ## Parse config and set defaults
    config_obj = eval(config_string, {}, {})
    if not isinstance(config_obj, dict):
        raise RuntimeError("Invalid plugin configuration: should be a single dict.")
    config = {
        # ALIASES_BEFORE  : config_obj.pop('aliases_before'  , ['splitBefore']),
        'aliases_after'   : config_obj.pop('aliases_after'   , ['splitAfter', 'split']),
        'alias_seperator' : config_obj.pop('aliases_after'   , '-'),
        'default_duration': config_obj.pop('default_duration', 'Month'),
        'default_step'    : config_obj.pop('default_step'    , 'Day'),
        'min_value' : D(str(config_obj.pop('min_value'       , 0.05))),
        'max_new_tx'      : config_obj.pop('max_new_tx'      , 9999),
        'suffix'          : config_obj.pop('suffix'          , ' (split %d/%d)'),
        'tag'             : config_obj.pop('tag'             , 'splitted'),
    }

    newEntries = []
    trashbin = []
    for entry in filter_txns(entries):

        # Split at entry level only, so that it balances.
        pass

        # We are interested in only marked entries. TODO: ALIASES_BEFORE.
        params = extract_mark_entry(entry, config)
        if not params:
            continue

        # For selected entries add new entries.
        trashbin.append(entry)
        newEntries = newEntries + new_whole_entries(entry, params, distribute_over_period, config)

    for trash in trashbin:
        entries.remove(trash)

    return entries + newEntries, errors
