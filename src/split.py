__author__ = 'Akuukis <akuukis@kalvis.lv'

from beancount.core.amount import Amount
from beancount.core import data
from beancount.core.number import D

from .common_functions import check_aliases_entry
from .common_functions import distribute_over_period
from .common_functions import get_dates
from .common_functions import longest_leg

__plugins__ = ['split']


def get_entries(entry, params, config):

    period, closing_dates = get_dates(params, entry.date, config)

    all_amounts = [];
    for posting in entry.postings:
        all_amounts.append( distribute_over_period(period, posting.units.number, config) )

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
                narration=entry.narration + config['suffix']%(i+1, period),
                tags={config['tag']},
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
    for i, entry in enumerate(entries):

        if not hasattr(entry, 'postings'):
            continue

        # TODO: ALIASES_BEFORE
        params = check_aliases_entry(entry, config)
        if not params:
            continue

        trashbin.append(entry)
        newEntries = newEntries + get_entries(entry, params, config)

    for trash in trashbin:
        entries.remove(trash)

    return entries + newEntries, errors
