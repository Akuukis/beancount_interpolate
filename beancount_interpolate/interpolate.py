import math
import datetime

from beancount.core.amount import Amount
from beancount.core.data import filter_txns
from beancount.core.data import Posting
from beancount.core.number import D

from .common import extract_mark_tx
from .common import parse_mark
from .common import extract_mark_posting
from .common import new_filtered_entries
from .common import new_whole_entries
from .common import distribute_over_period
from .common import read_config

__plugins__ = ['interpolate']

def interpolate(entries, options_map, user_config_string=""):
    """
    Entry point for single plugin structure.
    Currently a wrapper around interpolate_subset that passes a selection of commands.

    Args:
        entries: list of entries to process
        options_map: map of beancount options
        config_string: the multicommand configuration object
    Returns:
        list of entries, options, and errors
    """
    default_config = {
        'recur': {
            'aliases_after': ['recurAfter', 'recur'],
            'alias_seperator': '-',
            'default_duration': 'inf',
            'default_step': 'Day',
            'max_new_tx': 9999,
            'min_value': 0.05,
            'tag': 'recurred',
            'suffix': ' (recur %d/%d)',
        },
        'split': {
            'aliases_after': ['splitAfter', 'split'],
            'alias_seperator': '-',
            'default_duration': 'Month',
            'default_step': 'Day',
            'max_new_tx': 9999,
            'min_value': 0.05,
            'suffix': ' (split %d/%d)',
            'tag': 'splitted'
        },
        'spread': {
            'aliases_after': ['spreadAfter', 'spread'],
            'alias_seperator': '-',
            'default_duration': 'Month',
            'default_step': 'Day',
            'max_new_tx': 9999,
            'min_value': 0.05,
            'tag': 'spreaded',
            'suffix': ' (spread %d/%d)',
            'account_assets': 'Assets:Current',
            'account_liab': 'Liabilities:Current'
        },
        'depr': {
            'aliases_after': ['deprAfter', 'depr'],
            'alias_seperator': '-',
            'default_duration': 'Year',
            'default_step': 'Day',
            'max_new_tx': 9999,
            'min_value': 0.05,
            'tag': 'depreciated',
            'suffix': ' (depr %d/%d)',
            'account_assets': 'Assets:Fixed',
            'account_liab': 'Liabilities:Fixed'
        }
    }

    user_config = get_config(user_config_string, default_config)

    return interpolate_subset(entries, options_map, user_config)

def get_config(user_config_string, default_config):

    user_config = {}
    if len(user_config_string) > 0:
        user_config = eval(user_config_string, {}, {})
    if not isinstance(user_config, dict):
        raise RuntimeError("Invalid plugin configuration: should be a single dict.")

    # Expand global options to all commands
    commands = default_config.keys()
    global_options = [key for key in user_config if key not in commands]
    for option in global_options:
        for command in commands:
            if command not in user_config:
                user_config[command] = {}
            if option not in user_config[command]:
                user_config[command][option] = user_config[option]
        del user_config[option]

    # Copy all default options that were unset by the user into the user config
    for command in commands:
        if command not in user_config.keys():
            #copy the whole configuration for that command
            user_config[command] = default_config[command]
        else:
            for option in default_config[command]:
                if option not in user_config[command].keys():
                    user_config[command][option] = default_config[command][option]

    return user_config


def interpolate_subset(entries, options_map, config_map):
    """
    Temporary helper function that supports both single- or multi-plugin
    structures for beancount_interpolate

    Args:
        entries: list of entries to process
        options_map: map of beancount options
        commands_to_config_map: map of commands to config
    Returns:
        tuple of lists of entries, options, and errors
    """

    commands_to_functions_map = {
        'recur': recur,
        'split': split,
        'spread': spread,
        'depr': depreciate
    }

    # Calling each plugin creates a new error stream, so need to collect them all and concatenate
    all_errors = []

    for command in config_map.keys():
        entries, command_errors = commands_to_functions_map[command](entries, options_map, config_map[command])
        all_errors.extend(command_errors)

    return entries, all_errors

#########################
#                       #
# Copied from recur.py  #
#                       #
#########################

def dublicate_over_period(params, default_date, value, config):
    begin_date, duration, step = parse_mark(params, default_date, config)
    period = math.floor( duration / step )

    if(period > config['max_new_tx']):
        period = config['max_new_tx']
        duration = period * step

    dates = []
    amounts = []
    date = begin_date
    while date < begin_date + datetime.timedelta(days=duration) and date <= datetime.date.today():
        amounts.append( D(str(value)) )
        dates.append(date)
        date = date + datetime.timedelta(days=step)

    return (dates, amounts)


def recur(entries, options_map, config):
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

    newEntries = []
    trashbin = []
    for tx in filter_txns(entries):

        # Recur at entry level only, so that it balances.
        pass

        # We are interested in only marked entries. TODO: ALIASES_BEFORE.
        params = extract_mark_tx(tx, config)
        if not params:
            continue

        # Need to remove plugin metadata because otherwise new_whole_entries will copy it
        # to generated transactions, which is not the behaviour described in the docs.
        # TODO: Remove if alias is used as well.
        if('recur' in tx.meta):
            tx.meta.pop('recur')

        # For selected entries add new entries.
        trashbin.append(tx)
        newEntries = newEntries + new_whole_entries(tx, params, dublicate_over_period, config)

    for trash in trashbin:
        entries.remove(trash)

    return entries + newEntries, errors

#########################
#                       #
# Copied from split.py  #
#                       #
#########################

def split(entries, options_map, config):
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

    newEntries = []
    trashbin = []
    for tx in filter_txns(entries):

        # Split at entry level only, so that it balances.
        pass

        # We are interested in only marked entries. TODO: ALIASES_BEFORE.
        params = extract_mark_tx(tx, config)
        if not params:
            continue

        # For selected entries add new entries.
        trashbin.append(tx)

        # Need to remove plugin metadata because otherwise new_whole_entries will copy it
        # to generated transactions, which is not the behaviour described in the docs.
        # TODO: Remove if alias is used as well. Should we just remove all metadata, even
        # that which is not associated with the plugin?  I guess the desired behaviour is
        # never specified anywhere.
        if('split' in tx.meta):
            tx.meta.pop('split')

        newEntries = newEntries + new_whole_entries(tx, params, distribute_over_period, config)

    for trash in trashbin:
        entries.remove(trash)

    return entries + newEntries, errors

#########################
#                       #
# Copied from spread.py #
#                       #
#########################

def distribute_over_period_negative(params, default_date, total_value, config):
    return distribute_over_period(params, default_date, -total_value, config)

def spread(entries, options_map, config):
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

        # For selected postings change the original.
        for i, new_account, params, posting in selected_postings:
            tx.postings.pop(i)
            tx.postings.insert(i, Posting(
                account=new_account,
                units=Amount(posting.units.number, posting.units.currency),
                cost=None,
                price=None,
                flag=None,
                meta=None))
        # Need to remove plugin metadata because otherwise new_filetered_entries will copy it
        # to generated transactions, which is not the behaviour described in the docs.
        # Needed to pass tests
        tx.meta.pop('spread', None)


        # For selected postings add new postings bundled into entries.
        if len(selected_postings) > 0:
            newEntries = newEntries + new_filtered_entries(tx, params, distribute_over_period_negative, selected_postings, config)

    return entries + newEntries, errors

##############################
#                            #
# Copied from depreciate.py  #
#                            #
##############################

def depreciate(entries, options_map, config):
    """
    Beancount plugin: Generates new entries to depreciate target posting over given period.

    Args:
      entries: A list of directives. We're interested only in the Transaction instances.
      options_map: A parser options dict.
      config_string: A configuration string in JSON format given in source file.
    Returns:
      A tuple of entries and errors.
    """
    print(config)

    errors = []

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

            posting.meta.pop('depr', None)

            print("here")
            for translation in config['translations']:
                if posting.account[0:len(translation)] == translation:
                    new_account = config['translations'][translation] + posting.account[len(translation):]
                    selected_postings.append( (i, new_account, params, posting) )

        # For selected postings no need to change the original.
        pass


        # For selected postings add new postings bundled into entries.
        if len(selected_postings) > 0:

            # Need to remove plugin metadata because otherwise new_filetered_entries will copy it
            # to generated transactions, which is not the behaviour described in the docs.
            # Needed to pass tests
            tx.meta.pop('depr', None)
            newEntries = newEntries + new_filtered_entries(tx, params, distribute_over_period, selected_postings, config)

    return entries + newEntries, errors
