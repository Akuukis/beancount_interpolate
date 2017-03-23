import datetime
import math
import re
from beancount.core.number import D


def check_aliases_posting(aliases, posting):
    for alias in aliases:
        if hasattr(posting, 'meta') and posting.meta and alias in posting.meta:
            return posting.meta[alias]
    return False


def check_aliases_entry(aliases, entry, seperator):
    for alias in aliases:
        if hasattr(entry, 'meta') and entry.meta and alias in entry.meta:
            return entry.meta[alias]
        if hasattr(entry, 'tags') and entry.tags:
            for tag in entry.tags:
                if tag[0:len(alias+seperator)] == alias+seperator or tag == alias:
                    return tag[len(alias+seperator):] or True
    return False


def distribute_over_duration(max_duration, total_value, MIN_VALUE):
    ## Distribute value over points. TODO: add new methods

    if(total_value > 0):
        def round_to(n):
            return math.floor(n*100)/100
    else:
        def round_to(n):
            return math.ceil(n*100)/100

    if(abs(total_value/max_duration) > abs(MIN_VALUE)):
        amountEach = total_value / max_duration
        duration = max_duration
    else:
        if(total_value > 0):
            amountEach = MIN_VALUE
        else:
            amountEach = -MIN_VALUE
        duration = math.floor( abs(total_value) / MIN_VALUE )

    amounts = [];
    accumulated_remainder = D(str(0));
    for i in range(duration):
        amounts.append( D(str(round_to(amountEach + accumulated_remainder))) )
        accumulated_remainder += amountEach - amounts[len(amounts)-1]

    return amounts


def get_dates(params, default_date, DEFAULT_PERIOD, MAX_NEW_TX):
    # Infer Duration, start and steps. Format: [123|KEYWORD] [@ YYYY-MM-DD]
    try:
        parts = re.findall("^(\s*?(\S+))?\s*?(@\s*?([0-9]{4})-([0-9]{2})-([0-9]{2}))?\s*?$", params)[0]

        try:
            begin_date = datetime.date(int(parts[3]), int(parts[4]), int(parts[5]))
        except:
            begin_date = default_date

        try:
            duration = int(parts[0])
        except:
                dictionary = {
                    'day': 1,
                    'week': 7,
                    'month': 30,
                    'year': 365
                }
                duration = dictionary[parts[0].lower()]
    except:
        begin_date = default_date
        try:
            duration = int(DEFAULT_PERIOD)
        except:
                dictionary = {
                    'day': 1,
                    'week': 7,
                    'month': 30,
                    'year': 365
                }
                duration = dictionary[DEFAULT_PERIOD.lower()]

    # Given a begin_date, find out all dates until today
    if(duration<=MAX_NEW_TX):  # TODO: MAX_NEW_TX
        step = 1
    else:
        step = math.ceil(duration/MAX_NEW_TX)

    dates = []
    d = begin_date
    while d < begin_date + datetime.timedelta(days=duration) and d <= datetime.date.today():
        dates.append(d)
        d = d + datetime.timedelta(days=step)

    return duration, dates


def longest_leg(all_amounts):
    firsts = []
    for amounts in all_amounts:
        firsts.append( abs(amounts[0]) )
    return firsts.index(max(firsts))

