import datetime
import calendar
import math
import re
from itertools import compress
from beancount.core.number import D
from beancount.core.amount import Amount, mul
from beancount.core.data import Transaction
from beancount.core import data
from beancount.parser import printer

from collections import namedtuple

def parse_entries(entries, valid_commands):

    ignored = []
    parsed = []
    errors = []

    for entry in entries:
        if isinstance(entry, data.Transaction) and hasattr(entry, 'meta') and entry.meta: 

            # Get the keys from entry.meta that are valid commands
            found_commands = [key in valid_commands for key in list(entry.meta.keys())]
            command_keys = list(compress(entry.meta.keys(), found_commands))

            try:
                if len(command_keys) == 0:
                    ignored.append(entry)
                elif len(command_keys) == 1:
                    command = command_keys[0]
                    mark = entry.meta[command]
                    dates = _parse_mark(entry.meta[command], entry.date)
                    parsed.append((command, dates, entry))
                elif len(command_keys) > 1:
                    raise SyntaxError("Multiple commands associated with transaction")
            except SyntaxError as e:
                errors.append(e)
                ignored.append(entry)
        else:
            ignored.append(entry)

    return (ignored, parsed, errors)


def _parse_mark(mark, txn_date):
    """
    Parse mark into list of dates

    Args:
        mark: string of mark, i.e. "month @ 2018-04".
    Returns:
        A list of datetime dates
    """
    # Parse strings a, b, and c from mark < a [@ b] [/ c] >
    #    b and c are optional, a is not 
    #    a, b, and c cannot include /, @, or whitespace characters
    #    whitespace is optional everywhere else
    RE_PARSING = re.compile(r"(?:^\s*([^@/\s]+)\s*)(?:@\s*([^@/\s]+)\s*)?(?:\/\s*([^@/\s]+)\s*)?$")

    matches = re.findall(RE_PARSING, mark)

    if len(matches) == 0:
        raise SyntaxError("RE parser found zero matches")
    if len(matches) > 1:
        raise SyntaxError("RE parser found more than one match")

    parts = matches[0]

    start_date = txn_date
    step = 1

    try:
        if parts[1]:
            start_date = datetime.date.fromisoformat(parts[1])
    except Exception as e:
        raise SyntaxError('Could not parse start date: ' + str(e))

    try:
        if parts[2]:
            step = _parse_length(parts[2])
    except Exception as e:
        raise SyntaxError('Could not parse start step: ' + str(e))

    end_date = None
    try:
        end_date = datetime.date.fromisoformat(parts[0])
    except Exception as e1:
        try:
            duration = _parse_length(parts[0])
            end_date = start_date + datetime.timedelta(days=(duration-1))
        except Exception as e2:
            raise SyntaxError('Could not parse end date <or> duration: ' + str(e1) + " <or> " + str(e2))


    dates = []
    date = start_date
    while date <= end_date:
        dates.append(date)
        date += datetime.timedelta(days=step)

    return dates

def _parse_length(int_or_string):
    """
    Parses integer length or keywords into number of days.

    Args:
        int_or_string: string with number or keyword.
    Returns:
        An integer number of days.
    """
    try:
        return int(int_or_string)
    except:
        pass

    try:
        dictionary = {
            'day': 1,
            'week': 7,
            'month': 30,  # TODO.
            'year': 365,  # TODO.
            'inf': 365*1000000,
            'infinite': 365*1000000,
            'max': 365*1000000
        }
        return dictionary[int_or_string.lower()]
    except:
        pass

    raise Exception('Invalid period: '+int_or_string)
