from pytest import fixture
from pytest_bdd import scenario, given, when, then, parsers

from collections import namedtuple
from datetime import date

from beancount.core.compare import hash_entry, includes_entries, excludes_entries
from beancount.loader import load_string
from beancount.parser import printer
from context import parser

ParserTestcase = namedtuple('ParserTestcase', ['result', 'correct', 'incorrect']) 

test_cases = [
    ParserTestcase(
        result=[date(2020,2,1), date(2020,2,2), date(2020,2,3), date(2020,2,4)],

        correct=[(date(2020,2,1), "2020-02-04"),
                (date(2020,2,1), "2020-02-04 @ 2020-02-01"),
                (date(2020,2,3), "2020-02-04 @ 2020-02-01"),
                (date(2020,2,1), "4"),
                (date(2020,2,1), "4 @ 2020-02-01"),
                (date(2020,2,3), "4 @ 2020-02-01")],

        incorrect=[(date(2020,2,1), "2020-02-05"),
                   (date(2020,2,1), "2020-02-05 / 2"),
                   (date(2020,2,1), "5"),
                   (date(2020,2,2), "4"),]),

    ParserTestcase(
        result=[date(2020,2,1), date(2020,2,8), date(2020,2,15), date(2020,2,22)],
        correct=[
            (date(2020,2,1), "2020-02-22 / 7"),
            (date(2020,2,1), "2020-02-22 / week"),
            (date(2020,2,1), "2020-02-22 / WeEk"),
            (date(2020,2,1), "2020-02-28 / WeEk"),
            (date(2020,2,1), "23 / Week"),
            (date(2020,2,1), "28 / Week"),
            (date(2020,2,2), "2020-02-22 @ 2020-02-01 / week"),
        ],
        incorrect=[
            (date(2020,2,2), "2020-02-22 / week"),
            (date(2020,2,1), "2020-02-21 / week"),
            (date(2020,2,1), "22 / Week"),
            (date(2020,2,1), "29 / Week"),
            (date(2020,2,1), "23"),
            (date(2020,2,1), "4")
        ]
    )]

def test_parser():

    for test_case in test_cases:
        for txn_date, mark in test_case.correct:
            parsed = []
            print("Parsing mark <{}> with default date <{}>.".format(mark, txn_date)) 
            try:
                parsed = parser._parse_mark(mark, txn_date)
            except Exception as e:
                print(e)

            assert parsed == test_case.result

        for txn_date, mark in test_case.incorrect:
            parsed = []
            print("Parsing mark <{}> with default date <{}>.".format(mark, txn_date)) 
            try:
                parsed = parser.parse_mark(mark, txn_date)
            except Exception as e:
                print(e)

            assert parsed != test_case.result
