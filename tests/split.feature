Feature: Split a transaction over a period

    Scenario: Split a transfer from chequing to savings over a period

        Given the following beancount transaction:
            ;
            2016-06-15 * "Me" "Set aside money for savings"
                split: "Year @ 2016-06-15"
                Assets:MyBank:Savings           730.00 EUR
                Assets:MyBank:Chequing           -730.00 EUR

        When the beancount-split plugin is executed

        Then the original transaction should be removed

        And 365 new transactions should be generated

        And the newly generated transactions should include:
            ;
            ; The sum of all the generated postings will equal the posting from
            ; the deleted transaction

            2016-06-15 * "Me" "Set aside money for savings (split 1/365)" #splitted
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR

            2016-06-16 * "Me" "Set aside money for savings (split 2/365)" #splitted
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR

            2016-06-17 * "Me" "Set aside money for savings (split 3/365)" #splitted
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR
            ;        .
            ;        .
            ;        .

            2017-06-14 * "Me" "Set aside money for savings (split 365/365)" #splitted
                Assets:MyBank:Savings              2.0 EUR
                Assets:MyBank:Chequing            -2.0 EUR