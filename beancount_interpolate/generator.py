from beancount.core.amount import Amount
from beancount.core import data
from beancount.core.number import D

import datetime

def new_txns(old_txn, dates, values_matrix):

    new_entries = []

    for i, date in enumerate(dates):

        if date > datetime.date.today():
            break

        # The postings values for the a new transaction based on the ith date
        # will be the i-th column in the matrix of new posting values
        new_posting_values = [row[i] for row in values_matrix]

        narration_suffix = " (interpolated {}/{})".format(i+1, len(dates))

        new_entries.append(_new_txn(old_txn, date, new_posting_values, narration_suffix))

    return new_entries

def _new_txn(old_txn, new_date, new_posting_values, narration_suffix):
    new_postings = []
    for old_posting, new_value in zip(old_txn.postings, new_posting_values):
        new_units = Amount(new_value, old_posting.units.currency)
        new_postings.append(copy_posting(old_posting, units=new_units))

    return copy_txn(old_txn,
                    date=new_date,
                    meta=data.new_metadata(__name__, 0),
                    narration=old_txn.narration + narration_suffix,
                    postings=new_postings)

def copy_posting(old_posting, account=None, units=None, cost=None, price=None, flag=None, meta=None):
    if not account:
        account = old_posting.account
    if not units:
        units = old_posting.units
    if not cost:
        cost = old_posting.cost
    if not price:
        price = old_posting.price
    if not flag:
        flag = old_posting.flag
    if not meta:
        meta = old_posting.meta
    return data.Posting(account, units, cost, price, flag, meta=None)

def copy_txn(old_txn,
                     meta=None,
                     date=None,
                     flag=None,
                     payee=None,
                     narration=None,
                     tags=None,
                     links=None,
                     postings=None):
    if not meta:
        meta = old_txn.meta
    if not date:
        date = old_txn.date
    if not flag:
        flag = old_txn.flag
    if not payee:
        payee = old_txn.payee
    if not narration:
        narration = old_txn.narration
    if not tags:
        tags = old_txn.tags
    if not links:
        links = old_txn.links
    if not postings:
        postings = old_txn.postings
    return data.Transaction(meta, date, flag, payee, narration, tags, links, postings)
