__author__ = 'Akuukis <akuukis@kalvis.lv'

import datetime
import re
import math

from beancount.core.amount import Amount, add, sub, mul, div
from beancount.core import data
from beancount.core.position import Position
from beancount.core.number import ZERO, D, round_to

from .common_functions import check_aliases_entry
from .common_functions import distribute_over_duration
from .common_functions import get_dates
from .common_functions import longest_leg

__plugins__ = ['split']


def get_entries(duration, closing_dates, entry, MIN_VALUE, SUFFIX, TAG):
    all_amounts = [];
    for posting in entry.postings:
        all_amounts.append( distribute_over_duration(duration, posting.units.number, MIN_VALUE) )

    accumulator_index = longest_leg(all_amounts)

    remainder = D(str(0));
    new_transactions = []
    for i in range(len(closing_dates)):
        postings = []

        doublecheck = [];
        for p, posting in enumerate(entry.postings):
            if i < len(all_amounts[p]):
                doublecheck.append(all_amounts[p][i])
        should_be_zero = sum(doublecheck)
        if should_be_zero != 0:
            all_amounts[accumulator_index][i] -= D(str(should_be_zero))
            remainder += should_be_zero

        for p, posting in enumerate(entry.postings):
            if i < len(all_amounts[p]):
                postings.append(data.Posting(
                    account=posting.account,
                    units=Amount(all_amounts[p][i], posting.units.currency),
                    cost=None,
                    price=None,
                    flag=posting.flag,
                    meta=None))

        if len(postings) > 0:
            e = data.Transaction(
                date=closing_dates[i],
                meta=entry.meta,
                flag=entry.flag,
                payee=entry.payee,
                narration=entry.narration + SUFFIX%(i+1, duration),
                tags={TAG},
                links=entry.links,
                postings=postings)
            new_transactions.append(e)

    return new_transactions


def split(entries, options_map, config_string):
    errors = []

    ## Parse config and set defaults
    config_obj = eval(config_string, {}, {})
    if not isinstance(config_obj, dict):
        raise RuntimeError("Invalid plugin configuration: should be a single dict.")
    ALIASES_BEFORE   = config_obj.pop('aliases_before'  , ['splitBefore'])
    ALIASES_AFTER    = config_obj.pop('aliases_after'   , ['splitAfter', 'split'])
    ALIAS_SEPERATOR  = config_obj.pop('aliases_after'   , '-')
    DEFAULT_PERIOD   = config_obj.pop('default_period'  , 'Month')
    DEFAULT_METHOD   = config_obj.pop('default_method'  , 'SL')
    MIN_VALUE        = config_obj.pop('min_value'       , 0.05)
    MAX_NEW_TX       = config_obj.pop('max_new_tx'      , 9999)
    SUFFIX           = config_obj.pop('suffix'          , ' (split %d/%d)')
    TAG              = config_obj.pop('tag'             , 'splitted')
    MIN_VALUE = D(str(MIN_VALUE))

    newEntries = []
    trashbin = []
    for i, entry in enumerate(entries):

        if not hasattr(entry, 'postings'):
            continue

        # TODO: ALIASES_BEFORE
        params = check_aliases_entry(ALIASES_AFTER, entry, ALIAS_SEPERATOR)
        if not params:
            continue

        trashbin.append(entry)
        total_duration, closing_dates = get_dates(params, entry.date, MAX_NEW_TX)
        newEntries = newEntries + get_entries(total_duration, closing_dates, entry, MIN_VALUE, SUFFIX, TAG)

    for trash in trashbin:
        entries.remove(trash)

    return entries + newEntries, errors
