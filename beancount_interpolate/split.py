__author__ = 'Akuukis <akuukis@kalvis.lv'

from beancount.core.amount import Amount
from beancount.core.data import filter_txns
from beancount.core.number import D

from .parser import find_marked
from .common import extract_mark_tx
from .common import parse_mark
from .common import distribute_over_period
from .common import new_whole_entries
from .common import read_config

__plugins__ = ['split']


def split(entries, options_map, config_string=""):
    """
    Beancount plugin: Dublicates all entry postings over time at fraction of value.

    Args:
      entries: A list of directives. We're interested only in the Transaction instances.
      options_map: A parser options dict.
      config_string: A configuration string in JSON format given in source file.
    Returns:
      A tuple of entries and errors.
    """

    errors = []

    ## Parse config and set defaults
    config_obj = read_config(config_string)
    config = {
        # ALIASES_BEFORE  : config_obj.pop('aliases_before'  , ['splitBefore']),
        'aliases_after'   : config_obj.pop('aliases_after'   , ['splitAfter', 'split']),
        'alias_seperator' : config_obj.pop('aliases_after'   , '-'),
        'default_duration': config_obj.pop('default_duration', 'Month'),
        'default_step'    : config_obj.pop('default_step'    , 'Day'),
        'min_value' : D(str(config_obj.pop('min_value'       , 0.05))),
        'max_new_tx'      : config_obj.pop('max_new_tx'      , 9999),
        'suffix'          : config_obj.pop('suffix'          , ' (split %d/%d)'),
        'tag'             : config_obj.pop('tag'             , 'splitted'),
    }

    unmarked, marked = find_marked(entries, config)

    newEntries = []
    trashbin = []
    for tx, period in marked:

        # Need to remove plugin metadata because otherwise new_whole_entries will copy it
        # to generated transactions, which is not the behaviour described in the docs.
        # TODO: Remove if alias is used as well. Should we just remove all metadata, even
        # that which is not associated with the plugin?  I guess the desired behaviour is
        # never specified anywhere.
        tx.meta.pop('split')

        newEntries = newEntries + new_whole_entries(tx, period, distribute_over_period, config)

    return unmarked + newEntries, errors
