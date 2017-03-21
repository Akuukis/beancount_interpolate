import datetime
import re

def parse_params(params, default_date):
    # Infer Duration, start and steps. Format: [123|KEYWORD] [@ YYYY-MM-DD]
    parts = re.findall("^(\s*?(\S+))?\s*?(@\s*?([0-9]{4})-([0-9]{2})-([0-9]{2}))?\s*?$", params)[0]
    try:
        start = datetime.date(int(parts[3]), int(parts[4]), int(parts[5]))
    except:
        start = default_date
    try: # TODO: DEFAULT_PERIOD
        duration = int(parts[0])
    except:
        dictionary = {
            'Day': 1,
            'Week': 7,
            'Month': 30,
            'Year': 365
        }
        duration = dictionary[parts[0]]

    return start, duration
