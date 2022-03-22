Feature: Split a transaction over a period

    Background: default
        Given this setup:
            2010-01-01 open Assets:MyBank:Savings
            2010-01-01 open Assets:MyBank:Chequing

    Scenario: Split a transfer from chequing to savings over a period
        When this transaction is processed by split:
            2016-06-15 * "Me" "Set aside money for savings"
                split: "Year @ 2016-06-15"
                Assets:MyBank:Savings           730.00 EUR
                Assets:MyBank:Chequing           -730.00 EUR

        Then should not error
        Then there should be total of 365 transactions
        Then the transactions should include:
            2016-06-15 * "Me" "Set aside money for savings (split 1/365)" #splitted
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR
            2016-06-16 * "Me" "Set aside money for savings (split 2/365)" #splitted
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR
            2016-06-17 * "Me" "Set aside money for savings (split 3/365)" #splitted
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR
            ;
            2017-06-14 * "Me" "Set aside money for savings (split 365/365)" #splitted
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR

    Scenario: Split persists tags
        When this transaction is processed by split:
            2016-06-15 * "Me" "Set aside money for savings" #hello-world #second
                split: "Year @ 2016-06-15"
                Assets:MyBank:Savings           730.00 EUR
                Assets:MyBank:Chequing           -730.00 EUR

        Then should not error
        Then there should be total of 365 transactions
        Then the transactions should include:
            2016-06-15 * "Me" "Set aside money for savings (split 1/365)" #splitted #hello-world #second
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR
            2016-06-16 * "Me" "Set aside money for savings (split 2/365)" #splitted #hello-world #second
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR
            2016-06-17 * "Me" "Set aside money for savings (split 3/365)" #splitted #hello-world #second
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR
            ;
            2017-06-14 * "Me" "Set aside money for savings (split 365/365)" #splitted #hello-world #second
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR

    Scenario: Split using a amount tag
        When this transaction is processed by split:
            2016-06-01 * "Me" "Set aside money three times" #split-3
                Assets:MyBank:Savings           30.00 EUR
                Assets:MyBank:Chequing         -30.00 EUR

        Then should not error
        Then there should be total of 3 transactions
        Then the transactions should include:
            2016-06-01 * "Me" "Set aside money three times (split 1/3)" #split-3 #splitted
                Assets:MyBank:Savings              10.0 EUR
                Assets:MyBank:Chequing            -10.0 EUR
            2016-06-02 * "Me" "Set aside money three times (split 2/3)" #split-3 #splitted
                Assets:MyBank:Savings              10.0 EUR
                Assets:MyBank:Chequing            -10.0 EUR
            2016-06-03 * "Me" "Set aside money three times (split 3/3)" #split-3 #splitted
                Assets:MyBank:Savings              10.0 EUR
                Assets:MyBank:Chequing            -10.0 EUR

    Scenario: Split using a period tag
        When this transaction is processed by split:
            2016-06-01 * "Me" "Set aside money for savings" #split-month
                Assets:MyBank:Savings           60.00 EUR
                Assets:MyBank:Chequing         -60.00 EUR

        Then should not error
        Then there should be total of 30 transactions
        Then the transactions should include:
            2016-06-01 * "Me" "Set aside money for savings (split 1/30)" #split-month #splitted
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR
            2016-06-02 * "Me" "Set aside money for savings (split 2/30)" #split-month #splitted
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR
            2016-06-03 * "Me" "Set aside money for savings (split 3/30)" #split-month #splitted
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR
            ;
            2016-06-30 * "Me" "Set aside money for savings (split 30/30)" #split-month #splitted
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR
