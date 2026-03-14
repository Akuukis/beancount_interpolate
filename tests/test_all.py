from pytest_bdd import scenarios
import datetime as dt
import time_machine

import conftest

traveller = time_machine.travel(dt.datetime(2030, 1, 1))
traveller.start()

scenarios('depreciate/depreciate.feature')
scenarios('recur/recur.feature')
scenarios('split/split.feature')
scenarios('spread/spread.feature')
