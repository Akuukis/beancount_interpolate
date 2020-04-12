Feature: Repeat a transaction recur over a period

    Scenario: Repeat a transfer from chequing to savings over a period

        Given the following beancount transaction:
            ;
            2016-06-15 * "Me" "Set aside money for savings"
                recur: "Year @ 2016-06-15"
                Assets:MyBank:Savings             10.00 EUR
                Assets:MyBank:Chequing           -10.00 EUR

        When the beancount-recur plugin is executed

        Then the original transaction should be removed

        And 365 new transactions should be generated

        And the newly generated transactions should include:
            ;
            2016-06-15 * "Me" "Set aside money for savings (recur 1/365)" #recurred
                Assets:MyBank:Savings              10.00 EUR
                Assets:MyBank:Chequing            -10.00 EUR

            2016-06-16 * "Me" "Set aside money for savings (recur 2/365)" #recurred
                Assets:MyBank:Savings              10.00 EUR
                Assets:MyBank:Chequing            -10.00 EUR

            2016-06-17 * "Me" "Set aside money for savings (recur 3/365)" #recurred
                Assets:MyBank:Savings              10.00 EUR
                Assets:MyBank:Chequing            -10.00 EUR
            ;        .
            ;        .
            ;        .

            2017-06-14 * "Me" "Set aside money for savings (recur 365/365)" #recurred
                Assets:MyBank:Savings              10.00 EUR
                Assets:MyBank:Chequing            -10.00 EUR