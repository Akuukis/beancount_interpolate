import datetime
import re

def get_dates(params, default_date, MAX_NEW_TX):
    # Infer Duration, start and steps. Format: [123|KEYWORD] [@ YYYY-MM-DD]
    parts = re.findall("^(\s*?(\S+))?\s*?(@\s*?([0-9]{4})-([0-9]{2})-([0-9]{2}))?\s*?$", params)[0]

    try:
        begin_date = datetime.date(int(parts[3]), int(parts[4]), int(parts[5]))
    except:
        begin_date = default_date

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

    # Given a begin_date, find out all dates until today
    if(duration<=MAX_NEW_TX):  # TODO: MAX_NEW_TX
        step = 1
    else:
        step = math.ceil(duration/MAX_NEW_TX)

    dates = []
    d = begin_date
    while d < begin_date + datetime.timedelta(days=duration) and d <= datetime.date.today():
        dates.append(d)
        d = d + datetime.timedelta(days=step)

    return duration, dates
