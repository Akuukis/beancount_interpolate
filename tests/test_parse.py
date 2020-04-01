from pytest import fixture
from pytest_bdd import scenario, given, when, then, parsers

from beancount.core.compare import hash_entry, includes_entries, excludes_entries
from beancount.loader import load_string
from beancount.parser import printer
from context import parser, common

#@fixture
#def output_txns():
#    """
#    A fixture used by the when and then steps.
#    Allows the "then" steps to access the output of the "when" step.
#
#    Returns:
#      A reference to an empty list.
#    """
#    return list()
#
#@given(parsers.parse('the following configuration:\n{config_string}'))
#def user_config(config_string):
#    return common.read_config(config_string)
#
#@scenario('parser.feature',
#          'Parse a mark into a period',
#          example_converters=dict(transaction_date=str, mark=str, period_start=str, period_length=int))
#def test_parse_period():
#    pass
#
#@given(parsers.parse('Given the transaction has a <date> and is marked with <mark>'))
#def date_and_mark(transaction_date, mark):
#    print(transaction_date, mark) 
#
#@when(parsers.parse('the mark is parsed into a period'))
#def parse_mark_into_period(transaction_date, mark):
#    print(transaction_date, mark) 
#
#@then(parsers.parse('the period should have a start date of <period_start>'))
#def correct_period_start_date(period_start):
#    print(period_start) 
#
#@then(parsers.parse('the period should have a length of <period_days>'))
#def correct_period_length(period_length):
#    print(period_length) 
