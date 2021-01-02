from pytest import fixture
from pytest_bdd import given, when, then, parsers

from beancount.core.data import Transaction
from beancount.core.compare import hash_entry, includes_entries, excludes_entries
from beancount.loader import load_string
from beancount.parser import printer
from beancount_plugin_utils import marked, BeancountError, test_utils

from context import recur, split, spread, depreciate


@fixture
def config():
    return ""

@fixture
def setup_txns_text():
    return ""

@fixture
def input_txns():
    return list()

@fixture
def output_txns():
    return list()

@fixture
def errors():
    return list()


@given(parsers.parse('this config:'
                     '{config}'))
def config_custom(config):
    return config

@given(parsers.parse('this setup:'
                     '{setup_txns_text}'))
def setup_txns(setup_txns_text):
    return setup_txns_text


@when(parsers.parse('this transaction is processed by {variant}:'
                    '{input_txn_text}'))
def is_processed(variant, input_txns, errors, config, input_txn_text, setup_txns_text, output_txns):
    input_txns[:], _, _ = load_string(setup_txns_text + input_txn_text)

    if variant == 'depr':
        prefix_plugin_text = 'plugin "beancount_interpolate.depreciate" "' + config.strip('\n') + '"\n'
    elif variant == 'recur':
        prefix_plugin_text = 'plugin "beancount_interpolate.recur" "' + config.strip('\n') + '"\n'
    elif variant == 'split':
        prefix_plugin_text = 'plugin "beancount_interpolate.split" "' + config.strip('\n') + '"\n'
    elif variant == 'spread':
        prefix_plugin_text = 'plugin "beancount_interpolate.spread" "' + config.strip('\n') + '"\n'
    elif variant == 'all':
        prefix_plugin_text = 'plugin "beancount_interpolate.depreciate" "' + config.strip('\n') + '"\n'
        prefix_plugin_text = prefix_plugin_text + 'plugin "beancount_interpolate.recur" "' + config.strip('\n') + '"\n'
        prefix_plugin_text = prefix_plugin_text + 'plugin "beancount_interpolate.split" "' + config.strip('\n') + '"\n'
        prefix_plugin_text = prefix_plugin_text + 'plugin "beancount_interpolate.spread" "' + config.strip('\n') + '"\n'
    else:
        raise RuntimeError('Unknown variant: "{}".'.format(variant))

    full_text = prefix_plugin_text + setup_txns_text + input_txn_text
    print('\nInput (full & raw):\n------------------------------------------------')
    print(full_text + '\n')
    output_txns[:], errors[:], _ = load_string(full_text)
    print('\nOutput (Transactions):\n------------------------------------------------\n')
    for txn in output_txns:
        print(printer.format_entry(txn))
    print('\nOutput (Errors):\n------------------------------------------------\n')
    for error in errors:
        print(printer.format_error(error))


@then(parsers.parse('that transaction should be modified:'
                    '{correctly_modified_txn_text}'))
def original_txn_modified(input_txns, output_txns, errors, correctly_modified_txn_text):
    # Get modified original transaction from output of plugin
    # The modified originial transaction will be the last in the list of output transactions
    try:
        last = input_txns[len(input_txns)-1]
        modified_txn = test_utils.strip_flaky_meta([txn for txn in output_txns if txn.date == last.date and txn.narration == last.narration][0])
    except IndexError as error:
        raise error
    # Get correctly modified original transaction from feature file
    correctly_modified_txn = test_utils.strip_flaky_meta(load_string(correctly_modified_txn_text)[0][-1])

    print(" ; RECEIVED:\n", printer.format_entry(modified_txn))
    print(" ; EXPECTED:\n", printer.format_entry(correctly_modified_txn))

    # Compare strings instead of hashes because that's an easy way to exclude filename & lineno meta.

    try:
        print("RECEIVED:\n", modified_txn)
        print("EXPECTED:\n", correctly_modified_txn)
        assert hash_entry(modified_txn) == hash_entry(correctly_modified_txn)

    except AssertionError:
        # Rethrow as a nicely formatted diff
        assert printer.format_entry(modified_txn) == '\n'+correctly_modified_txn_text+'\n'
        # But in case strings matches..
        raise Exception("Transactions do not match, although their printed output is equal. See log output.")

@then(parsers.parse('that transaction should not be modified'))
def tx_not_modified(input_txns, output_txns):
    original_txn = test_utils.strip_flaky_meta(input_txns[-1])
    modified_txn = test_utils.strip_flaky_meta(output_txns[len(input_txns)-1])
    try:
        assert hash_entry(original_txn) == hash_entry(modified_txn)
    except AssertionError:
        print("RECEIVED:", modified_txn)
        print("EXPECTED:", original_txn)
        # Rethrow as a nicely formatted diff
        assert printer.format_entry(modified_txn) == printer.format_entry(original_txn)
        # But in case strings matches..
        raise Exception("Transactions do not match, although their printed output is equal. See log output.")

@then(parsers.parse('should not error'))
def not_error(errors):
    assert len(errors) == 0

# @then(parsers.parse('should produce config error:'
#                     '{exception_text}'))
# def config_error(input_txns, errors, exception_text):
#     original_txn = input_txns[-1]
#     assert len(errors) == 1
#     expected_error = example_plugin.PluginExampleError(original_txn.meta, exception_text.strip('\n'), original_txn)
#     assert type(errors[0]) is type(expected_error)
#     assert errors[0].message == expected_error.message
#     assert errors[0].entry == None

# @then(parsers.parse('should produce plugin error:'
#                     '{exception_text}'))
# def plugin_error(input_txns, errors, exception_text):
#     original_txn = input_txns[-1]
#     assert len(errors) == 1
#     expected_error = example_plugin.PluginExampleError(original_txn.meta, exception_text.strip('\n'), original_txn)
#     assert type(errors[0]) is type(expected_error)
#     assert errors[0].message == expected_error.message
#     assert test_utils.strip_flaky_meta(errors[0].entry) == test_utils.strip_flaky_meta(expected_error.entry)

# @then(parsers.parse('should produce marked error:'
#                     '{exception_text}'))
# def marked_error(input_txns, errors, exception_text):
#     original_txn = input_txns[-1]
#     assert len(errors) == 1
#     expected_error = marked.PluginUtilsMarkedError(original_txn.meta, exception_text.strip('\n'), original_txn)
#     assert type(errors[0]) is type(expected_error)
#     assert errors[0].message == expected_error.message
#     assert test_utils.strip_flaky_meta(errors[0].entry) == test_utils.strip_flaky_meta(expected_error.entry)

# @then(parsers.parse('should produce beancount error:'
#                     '{exception_text}'))
# def beancount_error(input_txns, errors, exception_text, output_txns):
#     original_txn = input_txns[-1]
#     modified_txn = output_txns[-1]
#     assert len(errors) == 1
#     expected_error = BeancountError.BeancountError(original_txn.meta, exception_text.strip('\n'), original_txn)
#     assert errors[0].message == expected_error.message and errors[0].entry == modified_txn



@then(parsers.parse('there should be total of {correct_num_to_generate:d} transactions'))
def correct_num_txns_generated(output_txns, correct_num_to_generate):

    # Get transactions from output of plugin (should be tagged appropriately)
    transactions = [txn for txn in output_txns if isinstance(txn, Transaction)]

    assert len(transactions) == correct_num_to_generate

@then(parsers.parse('the transactions should include:'
                    '{correctly_generated_txn_text}'))
def newly_generated_txns(output_txns, correctly_generated_txn_text):

    # Get transactions from output of plugin (should be tagged appropriately)
    transactions = [txn for txn in output_txns if isinstance(txn, Transaction)]

    # Get correctly generated transactions from feature file
    correctly_generated_txns, _, _ = load_string(correctly_generated_txn_text)

    has_correct, missing_entries = includes_entries(correctly_generated_txns, transactions)

    print("Missing entries: {}".format(len(missing_entries)))

    assert has_correct
