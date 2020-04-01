# For testsuite, The Way is to use a simple (but explicit) path modification
# to resolve the package properly.
#
# Ref: https://docs.python-guide.org/writing/structure/#test-suite

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from beancount_interpolate import common, depreciate, recur, split, spread, parser, interpolate
