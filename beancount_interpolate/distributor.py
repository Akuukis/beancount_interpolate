import datetime as dt
import decimal

from beancount.core.amount import Amount
from beancount.core import data
from beancount.core.number import D
from beancount.parser import printer

from .common import read_config

        # Matrix of values for new postings by by original posting and date
        #       d1  d2  d3  ... dN
        # p1    v11 v12 v13 ... v1N
        # p2    v21 v22 v23 ... v1N
        # p3    v31 v32 v33 ... v1N
        # ...
        # pM    vM1 vM2 VM3 ... VMN

def round_to(decim):
    f = round(decim*100)/100
    return D("{:.2f}".format(f))

def distribute_whole_postings(postings, dates):
    def distribute_whole(dates, total_value):
        distribution = []
        for date in dates:
            distribution.append(total_value)

        return distribution

    matrix = []
    for posting in postings:
        matrix.append(distribute_whole(dates, posting.units.number))

    return matrix

def distribute_fraction_even_postings(postings, dates):
    def distribute_fraction_even(dates, total_value):
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

            accumulated_remainder -= adjusted_amount

            distribution.append(adjusted_amount)

            if(date > dt.date.today()):
                break

        return distribution

    matrix = []
    for posting in postings[0:-1]:
        matrix.append(distribute_fraction_even(dates, posting.units.number))

    last_posting_distribution = []
    for i in range(len(dates)):
        summation = 0
        for j in range(len(matrix)):
            summation += matrix[j][i]
        last_posting_distribution.append(-summation)

    matrix.append(last_posting_distribution)

    return matrix


