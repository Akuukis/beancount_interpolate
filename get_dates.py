import datetime

def get_dates(begin_date, total_duration, MAX_NEW_TX):
    """Given a begin_date, find out all dates until today"""
    dates = []

    if(total_duration<=MAX_NEW_TX):  # TODO: MAX_NEW_TX
        step = 1
    else:
        step = math.ceil(total_duration/MAX_NEW_TX)

    d = begin_date
    while d < begin_date + datetime.timedelta(days=total_duration) and d <= datetime.date.today():
        dates.append(d)
        d = d + datetime.timedelta(days=step)

    return dates
