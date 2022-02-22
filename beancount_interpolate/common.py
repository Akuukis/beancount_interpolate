import datetime
from dateutil.relativedelta import relativedelta
import re
from beancount.core.number import D
from beancount.core.amount import Amount, mul
from beancount.core.data import Transaction, new_metadata
from beancount.core.data import Posting

def round_to(n):
    return round(n*100)/100

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


def get_number_of_txn(begin_date, duration, step, max_txn=float('inf')):
    n_txn = 0
    end_date = begin_date + duration
    while begin_date + n_txn * step < end_date:
        n_txn += 1
        if n_txn > max_txn:
            break
    return n_txn


def extract_mark_tx(tx, config):
    """
    Extract mark from transaction, if any.

    Args:
        tx: transaction instance.
        config: A configuration string in JSON format given in source file.
    Returns:
        string of mark or False.
    """

    for alias in config['aliases_after']:
        if hasattr(tx, 'meta') and tx.meta and alias in tx.meta:
            return tx.meta[alias]
        if hasattr(tx, 'tags') and tx.tags:
            for tag in tx.tags:
                if tag[0:len(alias+config['alias_seperator'])] == alias+config['alias_seperator'] or tag == alias:
                    return tag[len(alias+config['alias_seperator']):] or ''
    return False

def parse_mark(mark, default_date, config):
    """
    Parse mark into date, duration and step.

    Args:
        mark: string of mark, i.e. "month @ 2018-04".
        default_date: date to fallback to.
        config: A configuration string in JSON format given in source file.
    Returns:
        A tuple of datetime date, integer duration and integer step.
    """

    try:
        parts = re.findall(RE_PARSING, mark)[0]
        if parts[1] and parts[2]:
            begin_date = datetime.date(int(parts[1]), int(parts[2]), int(parts[3]) or 1)
        else:
            begin_date = default_date

        if parts[0]:
            duration = parse_length(parts[0])
        else:
            duration = parse_length(config['default_duration'])
            
        try:
            begin_date + duration
        except OverflowError:
            duration = relativedelta(days=(datetime.datetime(datetime.MAXYEAR, 12, 31).date() - begin_date).days)

        if parts[4]:
            step = parse_length(parts[4])
        else:
            step = parse_length(config['default_step'])

    except Exception as e:
        # TODO: Error handling
        print('WARNING: Using defaults, because cannot parse mark "%s": %s'%(str(mark), str(e)))

        begin_date = default_date
        step = parse_length(config['default_step'])
        duration = parse_length(config['default_duration'])

    return begin_date, duration, step


# Infer Duration, start and steps. Spacing optinonal. Format: [123|KEYWORD] [@ YYYY-MM[-DD]] [/ step]
# 0. max duration, 1. year, 2. month, 3. day, 4. min step
RE_PARSING = re.compile(r"^\s*?([^-/\s]+)?\s*?(?:@\s*?([0-9]{4})-([0-9]{2})(?:-([0-9]{2}))?)?\s*?(?:\/\s*?([^-/\s]+)?\s*?)?$")
def distribute_over_period(params, default_date, total_value, config):
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

    begin_date, duration, step = parse_mark(params, default_date, config)
    period = get_number_of_txn(begin_date, duration, step, max_txn=config['max_new_tx'])

    if(period > config['max_new_tx']):
        period = config['max_new_tx']
        duration = period * step

    dates = []
    amounts = []
    accumulated_remainder = D(str(0))

    i = 0
    while (begin_date + i * step) < (begin_date + duration) and (begin_date + i * step) <= datetime.date.today():
        accumulated_remainder += total_value / period
        if(abs(round_to(accumulated_remainder)) >= abs(round_to(config['min_value']))):
            amount = D(str(round_to(accumulated_remainder)))
            accumulated_remainder -= amount
            amounts.append(amount)
            dates.append(begin_date + i * step)
        i += 1
        if(begin_date + i * step > datetime.date.today()):
            # If today is reached before begin_date + duration is reached,
            # add the remaining of total_value to the last amount
            if sum(amounts) != total_value:
                amounts[-1] += total_value - sum(amounts)
            break

    return (dates, amounts)


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
        max_days = (
            datetime.datetime(datetime.MAXYEAR, 12, 31).date() - datetime.datetime(datetime.MINYEAR, 1, 1).date()
        ).days
        dictionary = {
            'day': relativedelta(days=+1),
            'week': relativedelta(weeks=+1),
            'month': relativedelta(months=+1),
            'year': relativedelta(years=+1),
            'inf': relativedelta(days=+max_days),
            'infinite': relativedelta(days=+max_days),
            'max': relativedelta(days=+max_days)
        }
        return dictionary[int_or_string.lower()]
    except:
        pass

    raise Exception('Invalid period: '+int_or_string)


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
        if len(amounts) == 0:
            # Should not have empty postings, but if do then at least don't crash.
            firsts.append( 0 )
        else:
            firsts.append( abs(amounts[0]) )

    return firsts.index(max(firsts))


def new_filtered_entries(tx, params, get_amounts, selected_postings, config):
    """
    Beancount plugin: Dublicates all transaction's postings over time.

    Args:
      tx: A transaction instance.
      params: A parser options dict.
      get_amounts: A function, i.e. distribute_over_period.
      selected_postings: A list of postings.
      config: A configuration string in JSON format given in source file.
    Returns:
      An array of transaction entries.
    """

    all_pairs = []

    for _, new_account, params, posting in selected_postings:
        dates, amounts = get_amounts(params, tx.date, posting.units.number, config)
        all_pairs.append( (dates, amounts, posting, new_account) )

    map_of_dates = {}

    for dates, amounts, posting, new_account in all_pairs:

        for i in range( min(len(dates), len(amounts)) ):
            if(not dates[i] in map_of_dates):
                map_of_dates[dates[i]] = []

            amount = Amount(amounts[i], posting.units.currency)
            # Income/Expense to be spread
            map_of_dates[dates[i]].append(Posting(account=new_account,
                              units=amount,
                              cost=None,
                              price=None,
                              flag=posting.flag,
                              meta=new_metadata(tx.meta['filename'], tx.meta['lineno'])))

            # Asset/Liability that buffers the difference
            map_of_dates[dates[i]].append(Posting(account=posting.account,
                              units=mul(amount, D(-1)),
                              cost=None,
                              price=None,
                              flag=posting.flag,
                              meta=new_metadata(tx.meta['filename'], tx.meta['lineno'])))

    new_transactions = []
    for i, (date, postings) in enumerate(sorted(map_of_dates.items())):
        if len(postings) > 0:
            e = Transaction(
                date=date,
                meta=tx.meta,
                flag=tx.flag,
                payee=tx.payee,
                narration=tx.narration + config['suffix']%(i+1, len(dates)),
                tags={config['tag']},
                links=tx.links,
                postings=postings)
            new_transactions.append(e)

    return new_transactions


def new_whole_entries(tx, params, get_amounts, config):


    all_amounts = [];
    for posting in tx.postings:
        closing_dates, amounts = get_amounts(params, tx.date, posting.units.number, config)
        all_amounts.append( amounts )

    accumulator_index = longest_leg(all_amounts)

    remainder = D(str(0));
    new_transactions = []
    for i in range(len(closing_dates)):
        postings = []

        doublecheck = [];
        for p, posting in enumerate(tx.postings):
            if i < len(all_amounts[p]):
                doublecheck.append(all_amounts[p][i])
        should_be_zero = sum(doublecheck)
        if should_be_zero != 0:
            all_amounts[accumulator_index][i] -= D(str(should_be_zero))
            remainder += should_be_zero

        for p, posting in enumerate(tx.postings):
            if i < len(all_amounts[p]):
                postings.append(Posting(
                    account=posting.account,
                    units=Amount(all_amounts[p][i], posting.units.currency),
                    cost=None,
                    price=None,
                    flag=posting.flag,
                    meta=new_metadata(tx.meta['filename'], tx.meta['lineno'])))

        tags = frozenset({config['tag']})
        if hasattr(tx, 'tags') and tx.tags:
            tags = frozenset().union(*[tags, tx.tags])

        if len(postings) > 0:
            e = Transaction(
                date=closing_dates[i],
                meta=tx.meta,
                flag=tx.flag,
                payee=tx.payee,
                narration=tx.narration + config['suffix']%(i+1, len(closing_dates)),
                tags=tags,
                links=tx.links,
                postings=postings)
            new_transactions.append(e)

    return new_transactions

def read_config(config_string):
    if len(config_string) == 0:
        config_obj = {}
    else:
        config_obj = eval(config_string, {}, {})

    if not isinstance(config_obj, dict):
        raise RuntimeError("Invalid plugin configuration: should be a single dict.")
    return config_obj
