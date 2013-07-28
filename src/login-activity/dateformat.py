import calendar
from datetime import datetime, timedelta

def utc_to_local(utc_dt_str):
    # get integer timestamp to avoid precision lost
    utc_dt = datetime.strptime(utc_dt_str, '%Y-%m-%dT%H:%M:%SZ')
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    return local_dt.strftime("%Y-%m-%d %H:%M:%S")
