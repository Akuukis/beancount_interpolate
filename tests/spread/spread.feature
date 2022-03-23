Feature: Spread income or expense postings over a period

    Scenario: Spread income from paycheque over pay period
        Given this setup:
            2010-01-01 open Income:TheCompany:NetSalary
            2010-01-01 open Liabilities:Current:TheCompany:NetSalary
            2010-01-01 open Assets:MyBank:Checking

        When this transaction is processed by spread:
            2016-06-15 * "The Company" "Salary for June"
                Income:TheCompany:NetSalary     -300.00 EUR
                    spread: "Month @ 2016-06-01"
                Assets:MyBank:Checking           300.00 EUR

        Then should not error
        Then there should be total of 31 transactions
        Then that transaction should be modified:
            2016-06-15 * "The Company" "Salary for June"
                Liabilities:Current:TheCompany:NetSalary       -300.00 EUR
                Assets:MyBank:Checking                          300.00 EUR
        Then the transactions should include:
            2016-06-01 * "The Company" "Salary for June (spread 1/30)" #spreaded
                Liabilities:Current:TheCompany:NetSalary         10.0 EUR
                Income:TheCompany:NetSalary                     -10.0 EUR
            2016-06-02 * "The Company" "Salary for June (spread 2/30)" #spreaded
                Liabilities:Current:TheCompany:NetSalary         10.0 EUR
                Income:TheCompany:NetSalary                     -10.0 EUR
            2016-06-03 * "The Company" "Salary for June (spread 3/30)" #spreaded
                Liabilities:Current:TheCompany:NetSalary         10.0 EUR
                Income:TheCompany:NetSalary                     -10.0 EUR
            ;
            2016-06-30 * "The Company" "Salary for June (spread 30/30)" #spreaded
                Liabilities:Current:TheCompany:NetSalary         10.0 EUR
                Income:TheCompany:NetSalary                     -10.0 EUR

    Scenario: Spread utility bill expenses over billing period
        Given this setup:
            2010-01-01 open Expenses:Bills:Internet
            2010-01-01 open Assets:MyBank:Checking
            2010-01-01 open Assets:Current:Bills:Internet

        When this transaction is processed by spread:
            2016-06-15 * "The Company" "Internet bill for June"
                Expenses:Bills:Internet                        -75.00 EUR
                    spreadAfter: "Month @ 2016-06-15"
                Assets:MyBank:Checking                          75.00 EUR

        Then should not error
        Then there should be total of 31 transactions
        Then that transaction should be modified:
            2016-06-15 * "The Company" "Internet bill for June"
                Assets:Current:Bills:Internet                  -75.00 EUR
                Assets:MyBank:Checking                          75.00 EUR
        Then the transactions should include:
            2016-06-15 * "The Company" "Internet bill for June (spread 1/30)" #spreaded
                Assets:Current:Bills:Internet                    2.5 EUR
                Expenses:Bills:Internet                         -2.5 EUR
            2016-06-16 * "The Company" "Internet bill for June (spread 2/30)" #spreaded
                Assets:Current:Bills:Internet                    2.5 EUR
                Expenses:Bills:Internet                         -2.5 EUR
            2016-06-17 * "The Company" "Internet bill for June (spread 3/30)" #spreaded
                Assets:Current:Bills:Internet                    2.5 EUR
                Expenses:Bills:Internet                         -2.5 EUR
            ;
            2016-07-14 * "The Company" "Internet bill for June (spread 30/30)" #spreaded
                Assets:Current:Bills:Internet                    2.5 EUR
                Expenses:Bills:Internet                         -2.5 EUR

    Scenario: Spread utility bill expenses over 3 days
        Given this setup:
            2010-01-01 open Expenses:Bills:Internet
            2010-01-01 open Assets:MyBank:Checking
            2010-01-01 open Assets:Current:Bills:Internet

        When this transaction is processed by spread:
            2016-06-15 * "The Company" "Internet bill for June"
                Expenses:Bills:Internet                        -75.00 EUR
                    spreadAfter: "3 @ 2016-06-15"
                Assets:MyBank:Checking                          75.00 EUR

        Then should not error
        Then there should be total of 4 transactions
        Then that transaction should be modified:
            2016-06-15 * "The Company" "Internet bill for June"
                Assets:Current:Bills:Internet                  -75.00 EUR
                Assets:MyBank:Checking                          75.00 EUR
        Then the transactions should include:
            2016-06-15 * "The Company" "Internet bill for June (spread 1/3)" #spreaded
                Assets:Current:Bills:Internet                   25.0 EUR
                Expenses:Bills:Internet                        -25.0 EUR
            2016-06-16 * "The Company" "Internet bill for June (spread 2/3)" #spreaded
                Assets:Current:Bills:Internet                   25.0 EUR
                Expenses:Bills:Internet                        -25.0 EUR
            2016-06-17 * "The Company" "Internet bill for June (spread 3/3)" #spreaded
                Assets:Current:Bills:Internet                   25.0 EUR
                Expenses:Bills:Internet                        -25.0 EUR

    Scenario: Spread utility bill expenses over 3 days with period
        Given this setup:
            2010-01-01 open Expenses:Bills:Internet
            2010-01-01 open Assets:MyBank:Checking
            2010-01-01 open Assets:Current:Bills:Internet

        When this transaction is processed by spread:
            2016-06-15 * "The Company" "Internet bill for June"
                Expenses:Bills:Internet                        -75.00 EUR
                    spreadAfter: "3 day @ 2016-06-15"
                Assets:MyBank:Checking                          75.00 EUR

        Then should not error
        Then there should be total of 4 transactions
        Then that transaction should be modified:
            2016-06-15 * "The Company" "Internet bill for June"
                Assets:Current:Bills:Internet                  -75.00 EUR
                Assets:MyBank:Checking                          75.00 EUR
        Then the transactions should include:
            2016-06-15 * "The Company" "Internet bill for June (spread 1/3)" #spreaded
                Assets:Current:Bills:Internet                   25.0 EUR
                Expenses:Bills:Internet                        -25.0 EUR
            2016-06-16 * "The Company" "Internet bill for June (spread 2/3)" #spreaded
                Assets:Current:Bills:Internet                   25.0 EUR
                Expenses:Bills:Internet                        -25.0 EUR
            2016-06-17 * "The Company" "Internet bill for June (spread 3/3)" #spreaded
                Assets:Current:Bills:Internet                   25.0 EUR
                Expenses:Bills:Internet                        -25.0 EUR

    Scenario: Spread utility bill expenses over 6 weeks bi-weekly
        Given this setup:
            2010-01-01 open Expenses:Bills:Internet
            2010-01-01 open Assets:MyBank:Checking
            2010-01-01 open Assets:Current:Bills:Internet

        When this transaction is processed by spread:
            2016-06-15 * "The Company" "Internet bill for June"
                Expenses:Bills:Internet                        -75.00 EUR
                    spreadAfter: "6 weeks @ 2016-06-15 / 2 weeks"
                Assets:MyBank:Checking                          75.00 EUR

        Then should not error
        Then there should be total of 4 transactions
        Then that transaction should be modified:
            2016-06-15 * "The Company" "Internet bill for June"
                Assets:Current:Bills:Internet                  -75.00 EUR
                Assets:MyBank:Checking                          75.00 EUR
        Then the transactions should include:
            2016-06-15 * "The Company" "Internet bill for June (spread 1/3)" #spreaded
                Assets:Current:Bills:Internet                   25.0 EUR
                Expenses:Bills:Internet                        -25.0 EUR
            2016-06-29 * "The Company" "Internet bill for June (spread 2/3)" #spreaded
                Assets:Current:Bills:Internet                   25.0 EUR
                Expenses:Bills:Internet                        -25.0 EUR
            2016-07-13 * "The Company" "Internet bill for June (spread 3/3)" #spreaded
                Assets:Current:Bills:Internet                   25.0 EUR
                Expenses:Bills:Internet                        -25.0 EUR
