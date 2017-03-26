import datetime
import math
import re
from beancount.core.number import D
from beancount.core.amount import Amount, mul
from beancount.core import data


def check_aliases_posting(posting, config):
    for alias in config['aliases_after']:
        if hasattr(posting, 'meta') and posting.meta and alias in posting.meta:
            return posting.meta[alias]
    return False


def check_aliases_entry(entry, config):
    for alias in config['aliases_after']:
        if hasattr(entry, 'meta') and entry.meta and alias in entry.meta:
            return entry.meta[alias]
        if hasattr(entry, 'tags') and entry.tags:
            for tag in entry.tags:
                if tag[0:len(alias+config['alias_seperator'])] == alias+config['alias_seperator'] or tag == alias:
                    return tag[len(alias+config['alias_seperator']):] or ''
    return False


def distribute_over_duration(max_duration, total_value, config):
    ## Distribute value over points. TODO: add new methods

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


def get_period(int_or_string):
    try:
        return int(int_or_string)
    except:
        pass

    try:
        dictionary = {
            'day': 1,
            'week': 7,
            'month': 30,
            'year': 365
        }
        return dictionary[int_or_string.lower()]
    except:
        pass

    raise Exception('Invalid period: '+int_or_string)


# Infer Duration, start and steps. Spacing optinonal. Format: [123|KEYWORD] [@ YYYY-MM[-DD]] [/ step]
# 0. max duration, 1. year, 2. month, 3. day, 4. min step
RE_PARSING = re.compile("^\s*?([^-/\s]+)?\s*?(?:@\s*?([0-9]{4})-([0-9]{2})(?:-([0-9]{2}))?)?\s*?(?:\/\s*?([^-/\s]+)?\s*?)?$")
def get_dates(params, default_date, config):
    try:
        parts = re.findall(RE_PARSING, params)[0]
        if parts[1] and parts[2]:
            begin_date = datetime.date(int(parts[1]), int(parts[2]), int(parts[3]) or 1)
        else:
            begin_date = default_date

        if parts[0]:
            duration = get_period(parts[0])
        else:
            duration = get_period(config['default_period'])

        if parts[4]:
            step = get_period(parts[4])
        else:
            step = get_period(config['default_step'])

    except Exception as e:
        # TODO: Error handling
        print('WARNING: Using defaults, because cannot parse params (%s): %s'%(str(params), str(e)))

        begin_date = default_date
        step = get_period(config['default_step'])
        duration = get_period(config['default_period'])

    period = math.floor( duration / step )

    if(period>config['max_new_tx']):
        step = math.floor(duration/config['max_new_tx'])
        duration = math.floor( get_period(config['default_period']) / step )

    dates = []
    d = begin_date
    while d < begin_date + datetime.timedelta(days=period) and d <= datetime.date.today():
        dates.append(d)
        d = d + datetime.timedelta(days=step)

    return period, dates


def longest_leg(all_amounts):
    firsts = []
    for amounts in all_amounts:
        firsts.append( abs(amounts[0]) )
    return firsts.index(max(firsts))


def new_filtered_entries(entry, selected_postings, params, config):
    all_amounts = []
    all_closing_dates = []
    for _ in entry.postings:
        all_amounts.append([])
        all_closing_dates.append([])

    for p, _, params, posting in selected_postings:
        total_periods, closing_dates = get_dates(params, entry.date, config)
        all_closing_dates[p] = closing_dates
        all_amounts[p] = distribute_over_duration(total_periods, posting.units.number, config)

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
    for date, postings in map_closing_dates.items():
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
