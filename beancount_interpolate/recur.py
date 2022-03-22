__author__ = 'Akuukis <akuukis@kalvis.lv>'
import datetime

from beancount.core.data import filter_txns
from beancount.core.number import D

from .common import extract_mark_tx
from .common import new_whole_entries
from .common import read_config
from .common import parse_mark
from .common import get_number_of_txn

__plugins__ = ['recur']


def duplicate_over_period(params, default_date, value, config):
    begin_date, duration, step = parse_mark(params, default_date, config)
    period = get_number_of_txn(begin_date, duration, step)

    if(period > config['max_new_tx']):
        period = config['max_new_tx']
        duration = period * step

    dates = []
    amounts = []
    i = 0
    end_date = begin_date + duration
    today_date = datetime.date.today()
    tmp_date = begin_date + i * step
    while tmp_date < end_date and tmp_date <= today_date:
        amounts.append(D(str(value)))
        dates.append(tmp_date)
        i += 1
        tmp_date = begin_date + i * step

    return (dates, amounts)


def recur(entries, options_map, config_string=""):
    """
    Beancount plugin: Duplicates all entry postings over time.

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

        if('recur' in tx.meta):
            tx.meta.pop('recur')

        for alias in config['aliases_after']:
            if alias in tx.tags:
                tx = tx._replace(
                    tags=tx.tags.difference([alias]),
                )

        newEntries = newEntries + new_whole_entries(tx, params, duplicate_over_period, config)

    for trash in trashbin:
        entries.remove(trash)

    return entries + newEntries, errors
