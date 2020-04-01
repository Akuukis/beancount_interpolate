import datetime as dt
import decimal

from beancount.core.amount import Amount
from beancount.core import data
from beancount.core.number import D
from beancount.parser import printer

from .parser import find_marked
from .parser import parse_mark
from .common import read_config

__plugins__ = ['interpolate']

def round_to(decim):
    f = round(decim*100)/100
    return D("{:.2f}".format(f))

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

    errors = []

    ignored, identified = find_marked(entries)

    new_entries = []
    for txn in identified:
        try:
            command, dates = parse_mark(txn.meta["interpolate"])
        except Exception as e:
            errors.append(e)
            ignored.append(txn)
            continue

        distributions = []
        for posting in txn.postings[:-1]:
            if command == 'split':
                distributions.append(distribute(dates, posting.units.number))
            elif command == 'recur':
                distributions.append(duplicate(dates, posting.units.number))

        last_posting_distribution = []
        for i in range(len(dates)):
            summation = 0
            for j in range(len(distributions)):
                summation += distributions[j][i]
            last_posting_distribution.append(-summation)

        distributions.append(last_posting_distribution)
            
        for i, date in enumerate(dates):

            new_postings = []

            for j, old_posting in enumerate(txn.postings):
                new_postings.append(data.Posting(
                    old_posting.account,
                    Amount(distributions[j][i], old_posting.units.currency),
                    old_posting.cost,
                    old_posting.price,
                    old_posting.flag,
                    old_posting.meta))
                
            new_entries.append(data.Transaction(
                date=date,
                meta=data.new_metadata(__name__, i),
                flag=txn.flag,
                payee=txn.payee,
                narration=txn.narration + " (interpolated {}/{})".format(i+1, len(dates)),
                tags=txn.tags,
                links=txn.links,
                postings=new_postings))

    for e in errors:
        print(e)

    printer.print_entries(new_entries)
    return ignored + new_entries, errors, options_map

def duplicate(dates, total_value):
    distribution = []
    for date in dates:
        distribution.append(total_value)

    return distribution

def distribute(dates, total_value):
    """
    Distribute value over points in time.

    Args:
        params: string of period.
        default_date: date to fallback to.
        total_value: decimal of total value.
        config: A configuration string in JSON format given in source file.
    Returns:
        A tuple of list of decimals and list of dates.
    """

    distribution = []
    accumulated_remainder = D(str(0))

    # The exact amount to be distributed over each day in the period before
    # rounding and other adjustments
    exact_amount = total_value/len(dates)

    for date in dates:
        accumulated_remainder += exact_amount

        adjusted_amount = round_to(accumulated_remainder)

        print(adjusted_amount)
        accumulated_remainder -= adjusted_amount

        distribution.append(adjusted_amount)

        if(date > dt.date.today()):
            break

    return distribution
