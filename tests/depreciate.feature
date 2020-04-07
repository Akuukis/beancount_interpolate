Feature: Depreciate assets over a period

    Scenario: Depreciate a purchase over a period

        Given the following beancount transaction:
            ;
            2016-06-15 * "CornerStore" "Bought new Laptop to do beancounting"
                Assets:Fixed:PC                  199.00 EUR
                    depr: "Year @ 2016-06-15"
                Assets:MyBank:Checking          -199.00 EUR

        When the beancount-depreciate plugin is executed

        Then the original transaction should be kept unmodified
        And 365 new transactions should be generated
        And the newly generated transactions should include:
            ;
            2016-06-15 * "CornerStore" "Bought new Laptop to do beancounting (depr 1/365)" #depreciated
                Assets:Fixed:PC                  -00.55 EUR
                Expenses:Depreciation:PC          00.55 EUR

            2016-06-16 * "CornerStore" "Bought new Laptop to do beancounting (depr 2/365)" #depreciated
                Assets:Fixed:PC                  -00.54 EUR
                Expenses:Depreciation:PC          00.54 EUR

            2016-06-17 * "CornerStore" "Bought new Laptop to do beancounting (depr 3/365)" #depreciated
                Assets:Fixed:PC                  -00.55 EUR
                Expenses:Depreciation:PC          00.55 EUR
            ;        .
            ;        .
            ;        .

            2017-06-14 * "CornerStore" "Bought new Laptop to do beancounting (depr 365/365)" #depreciated
                Assets:Fixed:PC                  -00.55 EUR
                Expenses:Depreciation:PC          00.55 EUR
