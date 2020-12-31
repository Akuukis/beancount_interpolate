Feature: Configure parser defaults and output format

    Scenario: Change the tag added for generated transactions

        Given the following configuration:
            {
                'tag': 'customtag'
            }

        And the following transaction:
            ;
            2020-01-01 * "Example transaction"
                recur: "5"
                Assets:Savings   10.00 USD
                Assets:Chequing

        Then the generated transactions should look like:
            ;
            2020-01-01 * "Example transaction (recur 1/5)" #customtag
                Assets:Savings   10.00 USD
                Assets:Chequing

    Scenario: Change the suffix added to the narration for generated transactions

        Given the following configuration:
            {
                'suffix': ' [CUSTOMSUFFIX %d out of %d]'
            }

        And the following transaction:
            ;
            2020-01-01 * "Example transaction"
                recur: "5"
                Assets:Savings   10.00 USD
                Assets:Chequing

        Then the generated transactions should look like:
            ;
            2020-01-01 * "Example transaction [CUSTOMSUFFIX 1 out of 5]" #recurred
                Assets:Savings   10.00 USD
                Assets:Chequing

    Scenario: Change the maximum number of transactions that can be generated

        Given the following configuration:
            {
                'max_new_tx': 1000
            }
        And the following transaction:
            ;
            2016-01-01 * "Example transaction"
                recur: "inf"
                Assets:Savings   1000.00 USD
                Assets:Chequing

        Then 1000 new transactions should be generated

    Scenario: Change the default duration used for parsing marks

        Given the following configuration:
            {
                'default_duration': 'Month'
            }
        And the following transaction:
            ;
            2020-01-01 * "Example transaction"
                recur: "/ 1"
                Assets:Savings   10.00 USD
                Assets:Chequing

        Then 30 new transactions should be generated

    Scenario: Change the default step used for parsing marks

        Given the following configuration:
            {
                'default_step': 2
            }

        And the following transaction:
            ;
            2020-01-01 * "Example transaction"
                recur: "4"
                Assets:Savings   10.00 USD
                Assets:Chequing

        Then the transactions generated should be:
            ;
            2020-01-01 * "Example transaction (recur 1/2)" #recurred
                Assets:Savings   10.00 USD
                Assets:Chequing

            2020-01-03 * "Example transaction (recur 2/2)" #recurred
                Assets:Savings   10.00 USD
                Assets:Chequing

    Scenario: Change the default minimum value used for distributing postings

        Given the following configuration:
            {
                'min_value': 0.10
            }
        And the following transaction:
            ;
            2020-01-01 * "Example transaction"
                split: "100"
                Assets:Savings   1.00 USD
                Assets:Chequing

        Then 10 new transactions should be generated

    Scenario: Change the liabilities account used by the spread command

        Given the following configuration:
            {
                'spread': {
                    'account_liab': 'Liabilities:Custom:Account'
                }
            }
        And the following transaction:
            ;
            2020-01-01 * "Example transaction"
                spread: "3"
                Assets:Chequing 300.00 USD
                Income:TempJob

        Then the transactions generated should be:
            ;
            2020-01-01 * "Example transaction"
                Assets:Chequing 300.00 USD
                Liabilities:Custom:Account:TempJob

            2020-01-01 * "Example transaction (spread 1/3)" #spreaded
                Liabilities:Custom:Account:TempJob   100.0 USD
                Income:TempJob

            2020-01-02 * "Example transaction (spread 2/3)" #spreaded
                Liabilities:Custom:Account:TempJob   100.0 USD
                Income:TempJob

            2020-01-03 * "Example transaction (spread 3/3)" #spreaded
                Liabilities:Custom:Account:TempJob   100.0 USD
                Income:TempJob

    Scenario: Change the assets account used by the depreciate command

        Given the following configuration:
            {
                'depr': {
                    'account_assets': 'Assets:Custom:Account'
                }
            }
        And the following transaction:
            ;
            2020-01-01 * "Example transaction"
                Assets:Custom:Account:ExampleItem
                    depr: "3"
                Assets:Chequing -300.00 USD

        Then the transactions generated should be:
            ;
            2020-01-01 * "Example transaction"
                Assets:Custom:Account:ExampleItem 300.00 USD
                Assets:Chequing

            2020-01-01 * "Example transaction (depr 1/3)" #depreciated
                Assets:Custom:Account:ExampleItem   -100.0 USD
                Expenses:Depreciation:ExampleItem

            2020-01-02 * "Example transaction (depr 2/3)" #depreciated
                Assets:Custom:Account:ExampleItem   -100.0 USD
                Expenses:Depreciation:ExampleItem

            2020-01-03 * "Example transaction (depr 3/3)" #depreciated
                Assets:Custom:Account:ExampleItem  -100.0 USD
                Expenses:Depreciation:ExampleItem
