from pytest import fixture
from pytest_bdd import scenario, given, when, then, parsers

from beancount.core.compare import hash_entry, includes_entries
from beancount.loader import load_string

from context import spread

@fixture
def output_txns():
    """
    A fixture used by the when and then steps.
    Allows the "then" steps to access the output of the "when" step.

    Returns:
      A reference to an empty list.
    """
    return list()

@scenario('spread.feature', 'Spread income from paycheque over pay period')
def test_spread_paycheque_():
    pass

@scenario('spread.feature', 'Spread utility bill expenses over billing period')
def test_spread_utilitybill_():
    pass

@given(parsers.parse('the following beancount transaction:\n{input_txn_text}'))
def input_txns(input_txn_text):
    input_txns, _, _ = load_string(input_txn_text)

    # Only one entry in feature file example
    assert len(input_txns) == 1
    return input_txns

@when(parsers.parse('the beancount-spread plugin is executed'))
def spread_txn(output_txns, input_txns):
    output_txns[:], _ = spread.spread(input_txns, {})

@then(parsers.parse('the original transaction should be modified:\n'
                    '{correctly_modified_txn_text}'))
def original_txn_modified(output_txns, correctly_modified_txn_text):

    # Get modified original transaction from output of plugin
    # The modified originial transaction will be the first in the list of output transactions
    modified_txn = output_txns[0]

    # Get correctly modified original transaction from feature file
    correctly_modified_txn = load_string(correctly_modified_txn_text)[0][0]

    assert hash_entry(modified_txn) == hash_entry(correctly_modified_txn)

@then(parsers.parse('{correct_num_to_generate:d} new transactions should be generated'))
def correct_num_txns_generated(output_txns, correct_num_to_generate):

    # The total number of output transactions should be the number of newly generated plus the
    # original modifed transaction
    assert len(output_txns) == correct_num_to_generate + 1
    

@then(parsers.parse('the newly generated transactions should include:\n'
                    '{correctly_generated_txn_text}'))
def newly_generated_txns(output_txns, correctly_generated_txn_text):

    # Get generated transactions from output of plugin
    # The generated transaction will be after the original modified transactions
    generated_txns = output_txns[1:]

    # Get correctly generated transactions from feature file
    correctly_generated_txns, _, _ = load_string(correctly_generated_txn_text)

    has_correct, _ = includes_entries(correctly_generated_txns, generated_txns)
    assert has_correct
