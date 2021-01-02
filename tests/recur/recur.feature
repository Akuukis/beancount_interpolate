Feature: Repeat a transaction recur over a period

    Background: default
        Given this setup:
            2010-01-01 open Assets:MyBank:Savings
            2010-01-01 open Assets:MyBank:Chequing

    Scenario: Repeat a transfer from chequing to savings over a period
        When this transaction is processed by recur:
            2016-06-15 * "Me" "Set aside money for savings"
                recur: "Year @ 2016-06-15"
                Assets:MyBank:Savings             10.00 EUR
                Assets:MyBank:Chequing           -10.00 EUR

        Then should not error
        Then there should be total of 365 transactions
        Then the transactions should include:
            2016-06-15 * "Me" "Set aside money for savings (recur 1/365)" #recurred
                Assets:MyBank:Savings              10.00 EUR
                Assets:MyBank:Chequing            -10.00 EUR
            2016-06-16 * "Me" "Set aside money for savings (recur 2/365)" #recurred
                Assets:MyBank:Savings              10.00 EUR
                Assets:MyBank:Chequing            -10.00 EUR
            2016-06-17 * "Me" "Set aside money for savings (recur 3/365)" #recurred
                Assets:MyBank:Savings              10.00 EUR
                Assets:MyBank:Chequing            -10.00 EUR
            ;
            2017-06-14 * "Me" "Set aside money for savings (recur 365/365)" #recurred
                Assets:MyBank:Savings              10.00 EUR
                Assets:MyBank:Chequing            -10.00 EUR
