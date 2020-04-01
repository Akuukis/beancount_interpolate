import datetime
import calendar
import math
import re
from beancount.core.number import D
from beancount.core.amount import Amount, mul
from beancount.core.data import Transaction
from beancount.core import data
from beancount.parser import printer

from collections import namedtuple

def find_marked(entries):

    ignored = []
    identified = []

    for entry in entries:
        if isinstance(entry, data.Transaction)\
           and hasattr(entry, 'meta') \
           and entry.meta \
           and "interpolate" in entry.meta:
                identified.append(entry)
        else:
            ignored.append(entry)

    return (ignored, identified)

RE_PARSING = re.compile(
    r"^([a-z]+)" # command
    "\s*?" # whitespace
    "([0-9]{4}-[0-9]{2}-[0-9]{2})" # date
    "\s*?-\s*?" # whitespace dash whitespace
    "([0-9]{4}-[0-9]{2}-[0-9]{2})" # date
)

def parse_mark(mark):
    """
    Parse mark into list of dates

    Args:
        mark: string of mark, i.e. "month @ 2018-04".
    Returns:
        A list of datetime dates
    """
    matches = re.findall(RE_PARSING, mark)

    if matches and len(matches[0]) == 3:
        command = matches[0][0]
        start = datetime.date.fromisoformat(matches[0][1])
        end = datetime.date.fromisoformat(matches[0][2])
    else:
        raise SyntaxError('Could not parse mark:', mark)


    dates = []
    delta = end - start
    for i in range(delta.days + 1):
        dates.append(start + datetime.timedelta(i))
    
    return (command, dates)

def parse_length(int_or_string):
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
