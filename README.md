Interpolate
===============================================================================

[![PyPI - Version](https://img.shields.io/pypi/v/beancount_interpolate)](https://pypi.org/project/packages/beancount_interpolate/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/beancount_interpolate)](https://pypistats.org/packages/beancount-interpolate)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/beancount_interpolate)
![PyPI - License](https://img.shields.io/pypi/l/beancount_interpolate)

Four plugins for double-entry accounting system Beancount to interpolate transactions by generating additional entries over time.

They are:
- `recur`: dublicates all entry postings over time
- `split`: dublicates all entry postings over time at fraction of value
- `depr`: generates new entries to depreciate target asset/liability posting over given period
- `spread`: generate new entries to allocate P&L of target income/expense posting over given period

These plugins are triggered by adding metadata or tags to source entries. It's safe to disable at any time. All plugins share the same parser that can set maximal period, custom starting date and minimal step by either number or keyword.

You can use these to define recurring transactions, account for depreciation, smooth transactions over time and make graphs less zig-zag.

> This `depr` is not yet compatible with any accounting standards. For tax-compatible yearly depreciation take a look at this [plugin](https://bitbucket.org/snippets/happyalu/EAMgj/beancount-automated-depreciation-plugin) by Alok Parlikar under MIT license. All contributions to improve `depr` are welcome.




Install
===============================================================================

```
pip3 install beancount_interpolate --user
```

Or copy to path used for python. For example, `$HOME/.local/lib/python3.7/site-packages/beancount_interpolate/*` would do on Debian. If in doubt, look where `beancount` folder is and copy next to it.




Details: Spread
===============================================================================

### Problem

Let's say John has only two activities

1. 10 EUR daily food expenses
2. 300 EUR net monthly salary (day 15 in next month)

If we plot John's wealth, it would look like zig-zag and be negative between -150 EUR (right after salary) and -450 EUR (right before), that is big and unstable error for your current wealth. And there could be more incomes/expenses with various 'periods'. In most complicated case John would have multiple income/expense sources with various lenght periods that are unsynchronised, but John wants dashboard with graph of correct daily report on his wealth.

Possible solutions:

1. Do nothing and ackowledge the 0-300 EUR error. IMO Is ok only if error is relatively small.
2. Do nothing and restrict yourself to do analysis at regular intervals when error is smallest (for example right after salary) and apply known corrections (for example, +150 EUR because it's already middle of month). IMO it is ok only if all periods are synchronised.
3. Record 10 EUR income to cash daily. But that violates 'after fact' principle that IMO is more important and IMO that's too much effort and transaction spam.
4. Record 10 EUR income to 'work token' assets daily but IMO that's still too much effort and transaction spam.
5. Let plugin do No.4 for you. (This repository)

### How to use

Enable the plugin (see available options below).

```beancount
plugin "beancount_interpolate.spread"
```

Add meta or tags to your transactions. All folllowing transactions does the same.

```
; Explicit.
2016-06-15 * "The Company" "Simplest salary entry"
    Income:TheCompany:NetSalary     -310.00 EUR
        spreadAfter: "Month @ 2016-05-01"
    Assets:MyBank:Checking           310.00 EUR

; Transaction meta applies to all Income/Expense postings if they don't have their own.
2016-06-15 * "The Company" "Simplest salary entry"
    spreadAfter: "Month @ 2016-05-01"
    Income:TheCompany:NetSalary     -310.00 EUR
    Assets:MyBank:Checking           310.00 EUR

; Use spreadBefore if that reads better in your case.
2016-06-15 * "The Company" "Simplest salary entry"
    spreadBefore: "Month @ 2016-05-31"
    Income:TheCompany:NetSalary     -310.00 EUR
    Assets:MyBank:Checking           310.00 EUR

; Use default period.
2016-06-15 * "The Company" "Simplest salary entry"
    spreadAfter: "2016-05-01"
    Income:TheCompany:NetSalary     -310.00 EUR
    Assets:MyBank:Checking           310.00 EUR

; Use date of transaction.
2016-06-15 * "The Company" "Simplest salary entry"
    spreadAfter: "Month"
    Income:TheCompany:NetSalary     -310.00 EUR
    Assets:MyBank:Checking           310.00 EUR

; Use date of transaction and default period. Beware the different transaction date.
2016-05-01 * "The Company" "Simplest salary entry" #spreadAfter
    Income:TheCompany:NetSalary     -310.00 EUR
    Assets:MyBank:Checking           310.00 EUR
```

### What happens

First, plugin edits the original transaction like this:

```
2016-05-01 * "The Company" "Simplest salary entry (Generated by interpolate-spread)" #spread
    Liabilities:Current:TheCompany:NetSalary       -310.00 EUR
    Assets:MyBank:Checking                          310.00 EUR
```

Second, plugin inserts 30 or 31 transactions from 2016-05-01 to 2016-05-31 like this:

```
2016-05-xx * "The Company" "Simplest salary entry (Generated by interpolate-spread)" #spread
    Income:TheCompany:NetSalary                     -10.00 EUR
    Liabilities:Current:TheCompany:NetSalary         10.00 EUR
```




Details: Recur
===============================================================================

### Problem

You want to make recurring entry every X days until forever (or some Y days have passed). Recur will duplicate tagged entry for you!

### How to use

Enable the plugin (see available options below).

```beancount
plugin "beancount_interpolate.recur"
```




Details: Split
===============================================================================

### Problem

In fact, the argumentation is the same as in `spread`, but the only difference is that different usecases needs a bit different treatment. For example, our John want to set aside money for savings daily. To account for it nicely, `spread` won't do - we don't need any `Liabilities:Current:...` accounts generated for us. A simple duplication will do here.

### How to use

Enable the plugin (see available options below).

```beancount
plugin "beancount_interpolate.split"
```

Add meta or tags to your transactions. All folllowing transactions does the same.

```
; Explicit.
2016-01-01 * "Me" "Set aside money for savings"
    split: "Year"
    Assets:MyBank:Checking          -365.00 EUR
    Assets:MyBank:Savings            365.00 EUR

; In fact, original date doesn't matter here, as original entry will be deleted.
2016-06-15 * "Me" "Set aside money for savings"
    splitAfter: "Year @ 2016-01-01"
    Assets:MyBank:Checking          -365.00 EUR
    Assets:MyBank:Savings            365.00 EUR


; Use can also use tags.
2016-01-01 * "Me" "Set aside money for savings" #split
    Assets:MyBank:Checking          -365.00 EUR
    Assets:MyBank:Savings            365.00 EUR
```

### What happens

First, plugin deletes the original transaction.

Second, plugin inserts transactions every day until today, included.

```
2016-01-01 * "Me" "Set aside money for savings (Generated by interpolate-split)" #split
    Assets:MyBank:Checking            -1.00 EUR
    Assets:MyBank:Savings              1.00 EUR

2016-01-02 * "Me" "Set aside money for savings (Generated by interpolate-split)" #split
    Assets:MyBank:Checking            -1.00 EUR
    Assets:MyBank:Savings              1.00 EUR

...
```




Details: Depreciate
===============================================================================

### Problem

Depreciate technically is the same as spread but from other way around. But practically, you would like to have different settings for your short-term spreads and long-term depreciations.

### How to use

Enable the plugin (see available options below).

```beancount
plugin "beancount_interpolate.depr"
```

Add meta or tags to your transactions. All folllowing transactions does the same.

```
; Explicit.
2016-06-15 * "CornerStore" "Bought new Laptop to do beancounting"
    Assets:Fixed:PC                  199.00 EUR
        depr: "Year @ 2016-06-15"
    Assets:MyBank:Checking          -199.00 EUR

; Transaction meta applies to all Assets:Fixed postings if depr is entry-wide.
2016-06-15 * "CornerStore" "Bought new Laptop to do beancounting"
    depr: "Year @ 2016-06-15"
    Assets:Fixed:PC                  199.00 EUR
    Assets:MyBank:Checking          -199.00 EUR


; Use default period (Year).
2016-06-15 * "CornerStore" "Bought new Laptop to do beancounting"
    depr: "Year"
    Assets:Fixed:PC                  199.00 EUR
    Assets:MyBank:Checking          -199.00 EUR

; Use date of transaction.
2016-06-15 * "CornerStore" "Bought new Laptop to do beancounting"
    depr: "Month"
    Assets:Fixed:PC                  199.00 EUR
    Assets:MyBank:Checking          -199.00 EUR

; Use default period (Year) and default date (entry date).
2016-06-15 * "CornerStore" "Bought new Laptop to do beancounting"
    depr: "empty string or some nonsense"
    Assets:Fixed:PC                  199.00 EUR
    Assets:MyBank:Checking          -199.00 EUR

; Use default period (Year) and default date (entry date) using a tag.
2016-06-15 * "CornerStore" "Bought new Laptop to do beancounting" #depr
    Assets:Fixed:PC                  199.00 EUR
    Assets:MyBank:Checking          -199.00 EUR
```

### What happens

Plugin inserts lots of transactions starting from given date until end (or today) like this:

```
2016-06-15 * "CornerStore" "Bought new Laptop to do beancounting (depr 1/365)" #depred
    Assets:Fixed:PC                  -00.55 EUR
    Expenses:Depreciation:PC          00.55 EUR

2016-06-16 * "CornerStore" "Bought new Laptop to do beancounting (depr 2/365)" #depred
    Assets:Fixed:PC                  -00.54 EUR
    Expenses:Depreciation:PC          00.54 EUR
```




Options
===============================================================================

In Beancount, options are passed to plugins as second argument and may be multi-line.
To `beancount_interpolate` options have to be formatted as valid JSON.

Options that applies to all four plugins:

* `aliases_after` - list of strings to look for in meta and tags.
* `default_duration` - integer or string of keyword that plugin will default duration to, if none was provided in mark.
* `default_step` - integer that plugin will default step to, if none was provided in mark.
* `min_value` - decimal that will be the minimal value of leg within created transactions.
* `max_new_tx` - integer that will be the maximal amount of newly created transactions.
* `suffix` - string appended to created transaction annotations. Two variables are n-th transaction and total amount of transactions.
* `tag` - string that as tag will be applied to all created transactions.

Options that applies only to `spread` and `depr`. For `spread` new transactions are created under account name where `account_expense` and `account_income` prefixes are swapped to `account_assets` or `account_liab` prefixes respectively. For `depr` that other way around: `account_assets` and `account_liab` prefixes are swapped to `account_expense` and `account_income` prefixes instead.
* `account_income`
* `account_expenses`
* `account_assets`
* `account_liab`

### Defaults

Here are all available options and their default values. Options are passed as serialized object to the plugin.

```beancount
plugin "beancount_interpolate.recur" "{
    'aliases_after': ['recurAfter', 'recur'],
    'default_duration': 'Infinite',
    'default_step': 'Day',
    'default_method': 'SL',
    'min_value': 0.05,
    'max_new_tx': 9999,
    'suffix': ' (recur %d/%d)',
    'tag': 'recurred'
}"

plugin "beancount_interpolate.split" "{
    'aliases_after': ['splitAfter', 'split'],
    'default_duration': 'Month',
    'default_step': 'Day',
    'default_method': 'SL',
    'min_value': 0.05,
    'max_new_tx': 9999,
    'suffix': ' (split %d/%d)',
    'tag': 'splitted'
}"

plugin "beancount_interpolate.spread" "{
    'account_income': 'Income',
    'account_expenses': 'Expenses',
    'account_assets': 'Assets:Current',
    'account_liab': 'Liabilities:Current',
    'aliases_after': ['spreadAfter', 'spread'],
    'default_duration': 'Month',
    'default_step': 'Day',
    'default_method': 'SL',  # Straight Line
    'min_value': 0.05,  # cannot be smaller than 0.01
    'max_new_tx': 9999,
    'suffix': ' (spread %d/%d)',
    'tag': 'spreaded'
}"

plugin "beancount_interpolate.depr" "{
    'account_income': 'Income:Appreciation',
    'account_expenses': 'Expenses:Depreciation',
    'account_assets': 'Assets:Fixed',
    'account_liab': 'Liabilities:Fixed',
    'aliases_after': ['deprAfter', 'depr'],
    'default_duration': 'Year',
    'default_step': 'Day',
    'min_value': 0.05,  # cannot be smaller than 0.01
    'max_new_tx': 9999,
    'suffix': ' (depr %d/%d)',
    'tag': 'depred'
}"
```

### Details: `aliases_after`

* Type: list of strings

If any of aliases are found in transaction tag, transaction meta or posting meta, then the plugin will be applied.

### Details: `default_duration`

* Type: integer or string (one of keywords: day, week, month, year, inf, infinite, max)

Default duration to apply when one is not specified explicitly. Note that month and year keywords do not adapt to current period, but are simple constants (PR welcome!)

### Details: `default_step`

* Type: integer

Default step to apply when one is not specified explicitly. In fact, currently it is not possible to specify it explicitly on per-case basis (PR welcome!)

### Details: `min_value`

* Type: decimal
* Restrictions: no less than 0.01

Minimal value of leg when for new created transactions. It will try to do so Here's example how it works:

For example, you want to spread your groceries 10.00 USD over 7 days, but it apparently doesn't divide nicely. So,
* 1st day would get allocated 1.43 USD but -0.001429 is kept aside (10.00/7=1.428571).
* 2nd day would get allocated 1.43 USD but -0.002858 is kept aside (10.00/7=1.428571-0.001429=1.427142)
* 3rd day would get allocated 1.43 USD but -0.004287 is kept aside (10.00/7=1.428571-0.002858=1.425713)
* 4th day would get allocated *1.42* USD but +0.004284 is kept aside (10.00/7=1.428571-0.004287=1.424284)
* 5th day would get allocated 1.43 USD but +0.002855 is kept aside (10.00/7=1.428571+0.004284=1.432855)
* 6th day would get allocated 1.43 USD but +0.001426 is kept aside (10.00/7=1.428571+0.002855=1.431426)
* 7th day would get allocated 1.43 USD and only pure rounding error is kept aside (10.00/7=1.428571+0.001426=1.429997)


The `min_value` is required to be at least 0.01 by beancount, but I'd recommend to raise it even further to avoid "1-cent spam" that lowers readability of reports and impacts performance.

There's an interesting behavior for transactions that are very small. If on any day the allocation is smaller by `min_value` for any of legs, the transaction on that day is not generated and put aside in full. Thus, such small transactions tend to happen once in a while with `min_value` amount. Even more funny, if there are more than one posting with small amount, those postings keep their "put aside" values seperaly - it may happen that at some day there will be a transaction with both of postings, effectively giving double of `min_value`. It may be hard to those little postings in reports, and I doubt that anyone would care about them at all, the best place to look at is the source.


### Details: `max_new_tx`

* Type: integer

Caps the max new transactions generated for one entry. By default set to 9999, looks like working but is not tested.


### Details: `suffix`

* Type: string

Suffix is string appended to created transaction annotations. It has two variables within in the given order:
1. n-th transaction
2. total amount of transactions.

### Details: `tag`

* Type: string

String that as tag will be applied to all created transactions.








Development
===============================================================================

The source contains five files - one per plugin and commons. Plugins have very similar structure in pairs: spread is similar to depreciate, and recur is similar to split.

Please see Makefile and inline comments.

Note: there's a branch `single-plugin-refactor` that's a up-for-grabs WIP based on v2 by [@benedictvh](https://github.com/benedictvh). See #8 #9, #12 for details.








See Also
===============================================================================

| Source                                                                                                                                                  | Author        | git | tests | Updated | PyPI                                                                                                                                      | Docs                                                                                                                                       | Comment                                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- | :-: | :---: | ------- | ----------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`beancount_interpolate.depr`](https://github.com/Akuukis/beancount_interpolate)                                                                        | Akuukis       |  ✅  |   ✅   | 2021-01 | [![beancount_interpolate](https://img.shields.io/pypi/v/beancount_interpolate)](https://pypi.org/project/packages/beancount_interpolate/) | [Readme](https://github.com/Akuukis/beancount_interpolate)                                                                                 |                                                                                                                                                                                                      |
| [`parallel_average_cost`](https://hub.darcs.net/falsifian/misc-pub/browse/beancount_plugins/falsifian/parallel_average_cost.py)                         | Falsifian     |  ❌  |   ✅   | 2021-03 | ❌                                                                                                                                         | [Discussion](https://groups.google.com/g/beancount/c/UcEqxDKtqB8/m/BJe_XFSlDAAJ)                                                           | This plugin is intended to help when you need to calculate your capital gains in two different ways, and one of them is average-cost booking.                                                        |
| [`auto_depreciation`](https://github.com/hktkzyx/auto_depreciation)                                                                                     | hktkzyx       |  ✅  |   ✅   | 2020-03 | ❌                                                                                                                                         | [Docs](https://hktkzyx.github.io/auto_depreciation/)                                                                                       |                                                                                                                                                                                                      |
| [`amortize_over`](https://gist.github.com/cdjk/0b8da9e2cc2dee5f3887ab5160970faa)                                                                        | Cary Kempston |  ❌  |   ❌   | 2017-09 | ❌                                                                                                                                         | [Discussion](https://beancount.narkive.com/PmCMMVPq/depreciation-plugin#post3)                                                             |                                                                                                                                                                                                      |
| [`flexible_deprecation`](https://github.com/davidastephens/beancount-plugins/blob/master/beancount_plugins/plugins/flexible_depreciation/depreciate.py) | Alok Parlikar |  ✅  |   ❌   | 2016-06 | [![beancount-plugins](https://img.shields.io/pypi/v/beancount-plugins)](https://pypi.org/project/packages/beancount-plugins/)             | [Docstring](https://github.com/davidastephens/beancount-plugins/blob/master/beancount_plugins/plugins/flexible_depreciation/depreciate.py) | Improved by Dave Stephens ([Discussion](https://groups.google.com/g/beancount/c/snPJqlswR5s/m/zaQ2g22jAQAJ)) and fixed by Akuukis ([PR](https://github.com/davidastephens/beancount-plugins/pull/3)) |
| [`split_transactions`](https://gist.github.com/kljohann/aebac3f0146680fd9aa5)                                                                           | Johann Klähn  |  ❌  |   ❌   | 2015-06 | ❌                                                                                                                                         | [Discussion](https://groups.google.com/g/beancount/c/z9sPboW4U3c/m/1qIIzro4zFoJ)                                                           |                                                                                                                                                                                                      |

Furthermore may look into the sources for inspiration of the related [DepreciateForLedger](https://github.com/tazzben/DepreciateForLedger).

And of course love (in form of backlink) to the [plaintextaccounting.org](https://plaintextaccounting.org).
