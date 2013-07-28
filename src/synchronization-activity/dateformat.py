import calendar
import time
from datetime import datetime, timedelta

def utc_to_local(utc_dt_str):
    # get integer timestamp to avoid precision lost
    utc_dt = datetime.strptime(utc_dt_str, '%Y-%m-%dT%H:%M:%SZ')
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    return local_dt.strftime("%Y-%m-%d %H:%M:%S")

def local_to_utc(local_dt_str):
    log_date = datetime.strptime(local_dt_str, '%Y-%m-%d %H:%M:%S')
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.mktime(log_date.timetuple())))

