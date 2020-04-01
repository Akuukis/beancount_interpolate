from pytest import fixture
from pytest_bdd import scenario, given, when, then, parsers

from beancount.core.compare import hash_entry, includes_entries, excludes_entries
from beancount.loader import load_string
from beancount.parser import printer
from context import spread, split

#
# Fixtures/steps used by all plugins
#

@fixture
def output_txns():
    """
    A fixture used by the when and then steps.
    Allows the "then" steps to access the output of the "when" step.

    Returns:
      A reference to an empty list.
    """
    return list()


@given(parsers.parse('the following beancount transaction:\n{input_txn_text}'))
def input_txns(input_txn_text):
    # Load the example beancount transaction from the feature file
    input_txns, _, _ = load_string(input_txn_text)

    # Only one entry in feature file example
    assert len(input_txns) == 1
    return input_txns

@then(parsers.parse('the original transaction should be modified:\n'
                    '{correctly_modified_txn_text}'))
def original_txn_modified(output_txns, correctly_modified_txn_text):

    # Get modified original transaction from output of plugin
    # The modified originial transaction will be the first in the list of output transactions
    modified_txn = output_txns[0]

    # Get correctly modified original transaction from feature file
    correctly_modified_txn = load_string(correctly_modified_txn_text)[0][0]

    print("Modified entry")
    printer.print_entry(modified_txn)

    print("Correctly modified entry")
    printer.print_entry(correctly_modified_txn)

    assert hash_entry(modified_txn) == hash_entry(correctly_modified_txn)


@then(parsers.parse('the original transaction should be removed'))
def original_txn_removed(input_txns, output_txns):
    """
    Check if the original transaction has been removed
    """
    removed, _ = excludes_entries(input_txns, output_txns)
    assert removed


@then(parsers.parse('{correct_num_to_generate:d} new transactions should be generated'))
def correct_num_txns_generated(output_txns, correct_num_to_generate):

    # Get newly generated transactions from output of plugin (should be tagged appropriately)
    generated_txns = [txn for txn in output_txns if
                      any(x in ["splitted", "spreaded"] for x in txn.tags)]

    assert len(generated_txns) == correct_num_to_generate

@then(parsers.parse('the newly generated transactions should include:\n'
                    '{correctly_generated_txn_text}'))
def newly_generated_txns(output_txns, correctly_generated_txn_text):

    # Get newly generated transactions from output of plugin (should be tagged appropriately)
    generated_txns = [txn for txn in output_txns if
                      any(x in ["splitted", "spreaded"] for x in txn.tags)]

    # Get correctly generated transactions from feature file
    correctly_generated_txns, _, _ = load_string(correctly_generated_txn_text)

    has_correct, missing_entries = includes_entries(correctly_generated_txns, generated_txns)

    print("Missing entries")
    printer.print_entries(missing_entries)

    assert has_correct

#
# Scenarios/steps for spread plugin
#
@scenario('spread.feature', 'Spread income from paycheque over pay period')
def test_spread_paycheque():
    pass

@scenario('spread.feature', 'Spread utility bill expenses over billing period')
def test_spread_utilitybill():
    pass

@when(parsers.parse('the beancount-spread plugin is executed'))
def spread_txn(output_txns, input_txns):
    output_txns[:], _ = spread.spread(input_txns, {})

#
# Scenarios/steps for split plugin
#
@scenario('split.feature', 'Split a transfer from chequing to savings over a period')
def test_split_transfer_to_savings():
    pass

@when(parsers.parse('the beancount-split plugin is executed'))
def split_txn(output_txns, input_txns):
    output_txns[:], _ = split.split(input_txns, {})
