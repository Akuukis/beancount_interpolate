Feature: Depreciate assets over a period

    Background: default
        Given this setup:
            2010-01-01 open Assets:Fixed:PC
            2010-01-01 open Assets:MyBank:Checking
            2010-01-01 open Expenses:Depreciation:PC

    Scenario: Depreciate a purchase over a period

        When this transaction is processed by depr:
            ;
            2016-06-15 * "CornerStore" "Bought new Laptop to do beancounting"
                Assets:Fixed:PC                  199.00 EUR
                    depr: "Week @ 2016-06-15"
                Assets:MyBank:Checking          -199.00 EUR

        Then should not error
        Then that transaction should not be modified
        Then there should be total of 8 transactions
        Then the transactions should include:
            2016-06-15 * "CornerStore" "Bought new Laptop to do beancounting (depr 1/7)" #depreciated
                Assets:Fixed:PC                  -28.43 EUR
                Expenses:Depreciation:PC          28.43 EUR
            2016-06-16 * "CornerStore" "Bought new Laptop to do beancounting (depr 2/7)" #depreciated
                Assets:Fixed:PC                  -28.43 EUR
                Expenses:Depreciation:PC          28.43 EUR
            2016-06-17 * "CornerStore" "Bought new Laptop to do beancounting (depr 3/7)" #depreciated
                Assets:Fixed:PC                  -28.43 EUR
                Expenses:Depreciation:PC          28.43 EUR
            2016-06-18 * "CornerStore" "Bought new Laptop to do beancounting (depr 4/7)" #depreciated
                Assets:Fixed:PC                  -28.42 EUR
                Expenses:Depreciation:PC          28.42 EUR
            ;
            2016-06-21 * "CornerStore" "Bought new Laptop to do beancounting (depr 7/7)" #depreciated
                Assets:Fixed:PC                  -28.43 EUR
                Expenses:Depreciation:PC          28.43 EUR
