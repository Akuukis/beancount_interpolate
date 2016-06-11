# Interpolate

Automatically add new transaction entries daily for two main cases:
* Depreciate Asset over period of time
* Spread Income/Expense over period of time

> For tax-compatible yearly depreciation take a look at this [plugin](https://bitbucket.org/snippets/happyalu/EAMgj/beancount-automated-depreciation-plugin) by Alok Parlikar under MIT license.

# Status

Works, but doesn't have most of options implemented. Expect it to be buggy, thus I would love to hear from you if you found a bug.

# Install

Copy to path used for python. For example, `$HOME/.local/lib/python3.5/site-packages/beancount_interpolate` would do on Debian. If in doubt, look where `beancount` folder is and copy next to it.

# Spread Expenses or Income over period of time

## Problem

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

## How to use

Copy/paste variables for plugin and edit for yourself.

```beancount
; Set defaults.
plugin "beancount_interpolate.spread" "{
    'account_income': 'Liabilities:Current',
    'account_expenses': 'Assets:Current',
    'aliases_before': ['spreadBefore'],
    'aliases_after': ['spreadAfter', 'spread'],
    'default_period': 'Month',
    'default_method': 'SL',  # Straight Line
    'min_value': 0.10,  # cannot be smaller than 0.01
    'max_new_tx': 182,
    'suffix': ' (Generated by interpolate-spread)',
    'tag': 'spread'
}"
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

## What happens

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

