import datetime as dt
import decimal

from beancount.core.amount import Amount
from beancount.core import data
from beancount.core.number import D
from beancount.parser import printer

from .parser import parse_entries
from .distribution import distribute_whole_postings, distribute_fraction_even_postings
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

def new_txn(old_txn, new_date, new_posting_values, narration_suffix):
    new_postings = []
    for old_posting, new_value in zip(old_txn.postings, new_posting_values):
        new_units = Amount(new_value, old_posting.units.currency)
        new_postings.append(data.Posting(
            old_posting.account,
            new_units, 
            old_posting.cost,
            old_posting.price,
            old_posting.flag,
            old_posting.meta))

    return data.Transaction(
        date=new_date,
        meta=data.new_metadata(__name__, 0),
        flag=old_txn.flag,
        payee=old_txn.payee,
        narration=old_txn.narration + narration_suffix,
        tags=old_txn.tags,
        links=old_txn.links,
        postings=new_postings)

def recur(txn, dates):

    values_matrix = distribute_whole_postings(txn.postings, dates)

    new_entries = []
    for i, date in enumerate(dates):

        # The postings values for the a new transaction based on the ith date
        # will be the i-th column in the matrix of new posting values
        new_posting_values = [row[i] for row in values_matrix]
        narration_suffix = " (interpolated {}/{})".format(i+1, len(dates))

        new_entries.append(new_txn(txn, date, new_posting_values, narration_suffix))

    return new_entries, []

def split(txn, dates):

    values_matrix = distribute_fraction_even_postings(txn.postings, dates)

    new_entries = []
    for i, date in enumerate(dates):

        # The postings values for the a new transaction based on the ith date
        # will be the i-th column in the matrix of new posting values
        new_posting_values = [row[i] for row in values_matrix]
        narration_suffix = " (interpolated {}/{})".format(i+1, len(dates))

        new_entries.append(new_txn(txn, date, new_posting_values, narration_suffix))

    return new_entries, []


def spread(txn, dates):
    pass

def depreciate():
    pass
