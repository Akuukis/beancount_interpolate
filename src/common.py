import datetime
import math
import re
from beancount.core.number import D
from beancount.core.amount import Amount, mul
from beancount.core import data


def extract_mark_posting(posting, config):
    """
    Extract mark from posting, if any.

    Args:
        posting: posting.
        config: A configuration string in JSON format given in source file.
    Returns:
        string of mark or False.
    """

    for alias in config['aliases_after']:
        if hasattr(posting, 'meta') and posting.meta and alias in posting.meta:
            return posting.meta[alias]
    return False


def extract_mark_entry(entry, config):
    """
    Extract mark from entry, if any.

    Args:
        entry: transaction entry.
        config: A configuration string in JSON format given in source file.
    Returns:
        string of mark or False.
    """

    for alias in config['aliases_after']:
        if hasattr(entry, 'meta') and entry.meta and alias in entry.meta:
            return entry.meta[alias]
        if hasattr(entry, 'tags') and entry.tags:
            for tag in entry.tags:
                if tag[0:len(alias+config['alias_seperator'])] == alias+config['alias_seperator'] or tag == alias:
                    return tag[len(alias+config['alias_seperator']):] or ''
    return False


def distribute_over_period(max_duration, total_value, config):
    """
    Distribute value over points in time.

    Args:
        max_duration: integer of duration.
        total_value: decimal of total value.
        config: A configuration string in JSON format given in source file.
    Returns:
        A list of decimals that sums up to total_value and is lenght of max_duration.
    """

    if(total_value > 0):
        def round_to(n):
            return math.floor(n*100)/100
    else:
        def round_to(n):
            return math.ceil(n*100)/100

    if(abs(total_value/max_duration) > abs(config['min_value'])):
        amountEach = total_value / max_duration
        duration = max_duration
    else:
        if(total_value > 0):
            amountEach = config['min_value']
        else:
            amountEach = -config['min_value']
        duration = math.floor( abs(total_value) / config['min_value'] )

    amounts = [];
    accumulated_remainder = D(str(0));
    for i in range(duration):
        amounts.append( D(str(round_to(amountEach + accumulated_remainder))) )
        accumulated_remainder += amountEach - amounts[len(amounts)-1]

    return amounts


def parse_length(int_or_string):
    """
    Parses length value or keywords into value.

    Args:
        int_or_string: string with number or keyword.
    Returns:
        A integer.
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


# Infer Duration, start and steps. Spacing optinonal. Format: [123|KEYWORD] [@ YYYY-MM[-DD]] [/ step]
# 0. max duration, 1. year, 2. month, 3. day, 4. min step
RE_PARSING = re.compile(r"^\s*?([^-/\s]+)?\s*?(?:@\s*?([0-9]{4})-([0-9]{2})(?:-([0-9]{2}))?)?\s*?(?:\/\s*?([^-/\s]+)?\s*?)?$")
def get_dates(params, default_date, config):
    """
    Find the longest leg between amounts.

    Args:
        params: string of period.
        default_date: date to fallback to.
        config: A configuration string in JSON format given in source file.
    Returns:
        A tuple of period and dates.
    """
    try:
        parts = re.findall(RE_PARSING, params)[0]
        if parts[1] and parts[2]:
            begin_date = datetime.date(int(parts[1]), int(parts[2]), int(parts[3]) or 1)
        else:
            begin_date = default_date

        if parts[0]:
            duration = parse_length(parts[0])
        else:
            duration = parse_length(config['default_duration'])

        if parts[4]:
            step = parse_length(parts[4])
        else:
            step = parse_length(config['default_step'])

    except Exception as e:
        # TODO: Error handling
        print('WARNING: Using defaults, because cannot parse params (%s): %s'%(str(params), str(e)))

        begin_date = default_date
        step = parse_length(config['default_step'])
        duration = parse_length(config['default_duration'])

    period = math.floor( duration / step )

    if(period>config['max_new_tx']):
        period = config['max_new_tx']
        duration = period * step

    dates = []
    d = begin_date
    while d < begin_date + datetime.timedelta(days=duration) and d <= datetime.date.today():
        dates.append(d)
        d = d + datetime.timedelta(days=step)

    return (period, dates)


def longest_leg(all_amounts):
    """
    Find the longest leg between amounts.

    Args:
        all_amounts: list of amounts.
    Returns:
        index of logest leg.
    """
    firsts = []
    for amounts in all_amounts:
        firsts.append( abs(amounts[0]) )
    return firsts.index(max(firsts))


def new_filtered_entries(entry, params, get_amounts, selected_postings, config):
    """
    Beancount plugin: Dublicates all entry postings over time.

    Args:
      entry: A transaction entry.
      params: A parser options dict.
      get_amounts: A function, i.e. distribute_over_period.
      selected_postings: A list of postings.
      config: A configuration string in JSON format given in source file.
    Returns:
      A array of transaction entries.
    """

    all_amounts = []
    all_closing_dates = []
    for _ in entry.postings:
        all_amounts.append([])
        all_closing_dates.append([])

    for p, _, params, posting in selected_postings:
        total_periods, closing_dates = get_dates(params, entry.date, config)
        all_closing_dates[p] = closing_dates
        all_amounts[p] = get_amounts(total_periods, posting.units.number, config)

    map_closing_dates = {}
    for closing_dates in all_closing_dates:
        for date in closing_dates:
            map_closing_dates[date] = []

    for p, new_account, _, posting in selected_postings:
        for i in range( min(len(all_closing_dates[p]), len(all_amounts[p])) ):
            amount = Amount(all_amounts[p][i], posting.units.currency)
            # Income/Expense to be spread
            map_closing_dates[all_closing_dates[p][i]].append(data.Posting(account=new_account,
                              units=amount,
                              cost=None,
                              price=None,
                              flag=posting.flag,
                              meta=None))

            # Asset/Liability that buffers the difference
            map_closing_dates[all_closing_dates[p][i]].append(data.Posting(account=posting.account,
                              units=mul(amount, D(-1)),
                              cost=None,
                              price=None,
                              flag=posting.flag,
                              meta=None))

    new_transactions = []
    for i, (date, postings) in enumerate(sorted(map_closing_dates.items())):
        if len(postings) > 0:
            e = data.Transaction(
                date=date,
                meta=entry.meta,
                flag=entry.flag,
                payee=entry.payee,
                narration=entry.narration + config['suffix']%(i+1, total_periods),
                tags={config['tag']},
                links=entry.links,
                postings=postings)
            new_transactions.append(e)

    return new_transactions


def new_whole_entries(entry, params, get_amounts, config):

    period, closing_dates = get_dates(params, entry.date, config)

    all_amounts = [];
    for posting in entry.postings:
        all_amounts.append( get_amounts(period, posting.units.number, config) )

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