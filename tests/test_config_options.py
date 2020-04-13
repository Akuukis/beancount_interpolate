from pytest import fixture
from pytest_bdd import scenario, given, when, then, parsers

from beancount.core.compare import hash_entry, includes_entries, excludes_entries, compare_entries
from beancount.loader import load_string
from beancount.parser import printer

from context import interpolate, recur, split, spread, depreciate

import json

@fixture
def multi_plugin_mode(pytestconfig):
    return pytestconfig.getoption("multiPluginMode")

@scenario('config_options.feature', 'Change the tag added for generated transactions')
def test_custom_tag():
    pass

@scenario('config_options.feature', 'Change the suffix added to the narration for generated transactions')
def test_custom_suffix():
    pass

@scenario('config_options.feature', 'Change the maximum number of transactions that can be generated')
def test_max_new_txn():
    pass

@scenario('config_options.feature', 'Change the default duration used for parsing marks')
def test_default_duration():
    pass

@scenario('config_options.feature', 'Change the default step used for parsing marks')
def test_default_step():
    pass

@scenario('config_options.feature', 'Change the default minimum value used for distributing postings')
def test_min_value():
    pass

@scenario('config_options.feature', 'Change the liabilities account used by the spread command')
def test_spread_account_assets():
    pass

@scenario('config_options.feature', 'Change the assets account used by the depreciate command')
def test_depreciate_account_assets():
    pass

@given(parsers.parse("the following configuration:\n{config_text}"))
def config_string(multi_plugin_mode, config_text):

    # Allows tests of plugin specific options to work in multi plugin mode as long as the config string
    # is of the form
    # {
    #     command: {
    #         option1': val1,
    #         ...
    #     }
    # }
    # with only one command and no global options given
    #
    # This hack is needed to run the same tests on both single- and multi- plugin modes
    # because there is an incompatability between the different modes in terms of configuration syntax
    # for options that are designed to only affect one plugin, like account_liab for the spread plugin
    if multi_plugin_mode:
        config_obj = eval(config_text, {}, {})
        if "spread" in config_obj:
            config_obj = config_obj["spread"]
        elif "depr" in config_obj:
            config_obj = config_obj["depr"]
        config_text = json.dumps(config_obj)

    return config_text

@given(parsers.parse("the following transaction:\n{txn_text}"))
def output_txns(config_string, txn_text):

    input_txn = load_string(txn_text)[0][0]

    output_txns = []

    if multi_plugin_mode:
        if "recur" in input_txn.meta:
            output_txns, _ = recur.recur([input_txn], {}, config_string)
        elif "split" in input_txn.meta:
            output_txns, _ = split.split([input_txn], {}, config_string)
        elif "spread" in input_txn.meta or any("spread" in posting.meta for posting in input_txn.postings):
            output_txns, _ = spread.spread([input_txn], {}, config_string)
        elif "depr" in input_txn.meta or any("depr" in posting.meta for posting in input_txn.postings):
            output_txns, _ = depreciate.depreciate([input_txn], {}, config_string)
    else:
        output_txns, _ = interpolate.interpolate(input_txn, {}, config_string)

    return output_txns

@then(parsers.parse("the generated transactions should look like:\n{txn_string}"))
def includes_correct_output_txns(output_txns, txn_string):
    correct_output_txns, _, _ = load_string(txn_string)
    printer.print_entries(correct_output_txns)

    printer.print_entries(output_txns)
    assert includes_entries(correct_output_txns, output_txns)[0]

@then(parsers.parse('{correct_num_to_generate:d} new transactions should be generated'))
def correct_num_txns_generated(output_txns, correct_num_to_generate):

    printer.print_entries(output_txns[:3])
    assert len(output_txns) == correct_num_to_generate 

@then(parsers.parse('the transactions generated should be:\n{txn_string}'))
def correct_output_txns(output_txns, txn_string):
    correct_output_txns, _, _ = load_string(txn_string)
    printer.print_entries(correct_output_txns)

    printer.print_entries(output_txns)
    assert compare_entries(correct_output_txns, output_txns)[0]
