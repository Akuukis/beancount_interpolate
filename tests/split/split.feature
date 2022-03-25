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

    Scenario: Split without losing cents
        When this transaction is processed by split:
            2016-06-01 * "Me" "Lost some pennies somewhere" #split-17
                Assets:MyBank:Savings             0.27 EUR
                Assets:MyBank:Chequing           -0.27 EUR

        Then should not error
        Then there should be total of 5 transactions
        Then the transactions should include:
            2016-06-03 * "Me" "Lost some pennies somewhere (split 1/5)" #split-17 #splitted
                Assets:MyBank:Savings    0.05 EUR
                Assets:MyBank:Chequing  -0.05 EUR

            2016-06-06 * "Me" "Lost some pennies somewhere (split 2/5)" #split-17 #splitted
                Assets:MyBank:Savings    0.05 EUR
                Assets:MyBank:Chequing  -0.05 EUR

            2016-06-10 * "Me" "Lost some pennies somewhere (split 3/5)" #split-17 #splitted
                Assets:MyBank:Savings    0.06 EUR
                Assets:MyBank:Chequing  -0.06 EUR

            2016-06-13 * "Me" "Lost some pennies somewhere (split 4/5)" #split-17 #splitted
                Assets:MyBank:Savings    0.05 EUR
                Assets:MyBank:Chequing  -0.05 EUR

            2016-06-17 * "Me" "Lost some pennies somewhere (split 5/5)" #split-17 #splitted
                Assets:MyBank:Savings    0.06 EUR
                Assets:MyBank:Chequing  -0.06 EUR

    Scenario: Split small amount over month
        When this transaction is processed by split:
            2020-06-01 * "shop" "cookies" #split-month
                Assets:MyBank:Chequing                           0.13 EUR
                Assets:MyBank:Savings                           -0.13 EUR

        Then should not error
        Then there should be total of 2 transactions
        Then the transactions should include:
            2020-06-11 * "shop" "cookies (split 1/2)" #split-month #splitted
                Assets:MyBank:Savings                           -0.05 EUR
                Assets:MyBank:Chequing                           0.05 EUR
            2020-06-22 * "shop" "cookies (split 2/2)" #split-month #splitted
                Assets:MyBank:Savings                           -0.08 EUR
                Assets:MyBank:Chequing                           0.08 EUR

    Scenario: Split amount below min_value over month
        When this transaction is processed by split:
            2020-06-01 * "shop" "cookies" #split-month
                Assets:MyBank:Chequing                           0.03 EUR
                Assets:MyBank:Savings                           -0.03 EUR

        Then should not error
        Then there should be total of 1 transactions
        Then the transactions should include:
            2020-06-01 * "shop" "cookies (split 1/1)" #split-month #splitted
                Assets:MyBank:Savings                           -0.03 EUR
                Assets:MyBank:Chequing                           0.03 EUR
