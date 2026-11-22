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

    Scenario: Recur a transaction with a priced posting
        Given this setup:
            2010-01-01 open Assets:MyBank:Checking RUB
            2010-01-01 open Expenses:Rent USD

        When this transaction is processed by recur:
            2016-06-15 * "Landlord" "Pay rent"
                recur: "2 Months / 1 Month"
                Assets:MyBank:Checking
                Expenses:Rent                       800 USD @ 61.46 RUB

        Then should not error
        Then there should be total of 2 transactions
        Then the transactions should include:
            2016-06-15 * "Landlord" "Pay rent (recur 1/2)" #recurred
                Assets:MyBank:Checking            -49168.00 RUB
                Expenses:Rent                       800 USD @ 61.46 RUB
            2016-07-15 * "Landlord" "Pay rent (recur 2/2)" #recurred
                Assets:MyBank:Checking            -49168.00 RUB
                Expenses:Rent                       800 USD @ 61.46 RUB
