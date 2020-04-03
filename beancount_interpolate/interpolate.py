import datetime as dt
import decimal

from beancount.core.amount import Amount
from beancount.core import data
from beancount.core.number import D
from beancount.parser import printer

from .parser import parse_entries
from .generator import new_txns, copy_posting, copy_txn
from .distributor import distribute_whole_postings, distribute_fraction_even_postings
from .common import read_config

__plugins__ = ['interpolate']

def interpolate(entries, options_map, config_string=""):
    """
    Beancount plugin: Generates transactions

    Args:
      entries: A list of directives. We're interested only in the Transaction instances.
      options_map: A parser options dict.
      config_string: A configuration string in JSON format given in source file.
    Returns:
      A tuple of entries and errors.
    """

    commands_map = {
        'recur': recur,
        'split': split,
        'spread': spread,
        'depr': depreciate
    }

    ignored_entries, parsed_entries, parsing_errors = parse_entries(entries, commands_map.keys())

    errors = parsing_errors
    new_entries = []
    for command, dates, txn in parsed_entries:
        generated_txns, generation_errors = commands_map[command](txn, dates)
        new_entries.extend(generated_txns)
        errors.extend(generation_errors)

    printer.print_entries(new_entries)
    return ignored_entries + new_entries, errors, options_map

def recur(txn, dates):
    values_matrix = distribute_whole_postings(txn.postings, dates)
    return new_txns(txn, dates, values_matrix), []

def split(txn, dates):
    values_matrix = distribute_fraction_even_postings(txn.postings, dates)
    return new_txns(txn, dates, values_matrix), []

def spread(txn, dates):

    updated_txn_postings = []
    template_postings = []
    for posting in txn.postings:
        # TODO if "interpolate" in posting.tags:
        if hasattr(posting, "meta") and "interpolate" in posting.meta.keys():
            new_account = posting.meta["interpolate"]
            template_postings.append(posting)
            template_postings.append(copy_posting(posting, account=new_account, units=-posting.units))
            updated_txn_postings.append(copy_posting(posting, account=new_account))
        else:
            updated_txn_postings.append(posting)

    template_txn = copy_txn(txn, postings=template_postings)
    new_entries, errors = split(template_txn, dates)

    new_narration = txn.narration + " (modified by interpolate)"
    updated_txn = copy_txn(txn, narration=new_narration, postings=updated_txn_postings)
    new_entries.append(updated_txn)

    return new_entries, errors
    
def depreciate():
    pass

def read_config(config_string):
    if len(config_string) == 0:
        config_obj = {}
    else:
        config_obj = eval(config_string, {}, {})

    if not isinstance(config_obj, dict):
        raise RuntimeError("Invalid plugin configuration: should be a single dict.")
    return config_obj
