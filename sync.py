from threading import Timer

from datetime import datetime
import pytz

timezone = pytz.UTC


def get_current_time():
    return datetime.now().astimezone(timezone)


def get_sync_secs(timeframe):
    now = get_current_time()

    diff_secs = 0

    if timeframe == "1s":
        diff_secs = 1

    if timeframe == "1M":
        diff_secs = 60 - now.second

    if timeframe == "2M":
        diff_secs = ((2 - (now.minute % 2)) * 60) - now.second
        # print("diff ", timeframe, now.minute, now.minute%2 , (now.minute % 2) * 60)
        # print("left over: ", now.second, now.minute%2 * 60 + 60 - now.second)

    if timeframe == "3M":
        diff_secs = ((3 - (now.minute % 3)) * 60) - now.second

    if timeframe == "4M":
        diff_secs = ((4 - (now.minute % 4)) * 60) - now.second

    if timeframe == "5M":
        diff_secs = ((5 - (now.minute % 5)) * 60) - now.second

    if timeframe == "6M":
        diff_secs = ((6 - (now.minute % 6)) * 60) - now.second

    if timeframe == "15M":
        diff_secs = ((15 - (now.minute % 15)) * 60) - now.second

    if timeframe == "30M":
        diff_secs = ((30 - (now.minute % 30)) * 60) - now.second

    if timeframe == "1H":
        diff_secs = 3600 - (now.minute * 60) - now.second

    if timeframe == "4H":
        diff_secs = (4 - (now.hour % 4)) * 3600 - (now.minute * 60) - now.second

    if timeframe == "1D":
        diff_secs = 86400 - (now.hour * 3600) - (now.minute * 60) - now.second

    return diff_secs


def poller(func, timeframe, adjust_secs=0):
    def wrapper():
        poller(func, timeframe, adjust_secs)
        func()

    secs = get_sync_secs(timeframe) + adjust_secs
    t = Timer(secs, wrapper)
    t.start()
    return t
