Feature: Parse a mark into a period

    Background:
        Given the following configuration:
        {
            'default_step': 'Day',
            'default_duration': 'Month'
        }

    Scenario Outline: Parse a mark into a period

        Given the transaction has a <date> and is marked with <mark>
        When the mark is parsed into a period
        Then the period should have a start date of <period_start>
        And the period should have a length of <period_days>

        Examples:
        | transaction_date | mark               | period_start | period_length |
        | 2016-06-15       |                    | 2016-06-15   | 30            |
        | 2016-06-15       | Year               | 2016-06-15   | 365           |
        | 2016-06-15       | Month              | 2016-06-15   | 365           |
        | 2016-06-15       | Week               | 2016-06-15   | 7             |
        | 2016-06-15       | Month @ 2016-06-01 | 2016-06-01   | 365           |
        | 2016-06-15       | Week @ 2016-06-01  | 2016-06-01   | 365           |
        | 2016-06-15       | Year @ 2016-06-01  | 2016-06-01   | 365           |