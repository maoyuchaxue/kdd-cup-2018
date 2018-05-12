import numpy as np

import time
import datetime

eps = 1e-4

def SMAPE(actual, pred):
    p = pred
    p[pred < 0] = 0
    return np.mean(np.abs(actual - p) / ((actual + p + eps) / 2.0))


def time_to_int(time_str):
    # convert timestring to timestamp(int) / 3600
    # %Y-%m-%d
    # %Y/%m/%d
    # %Y-%m-%d %H:%M:%S
    # %Y/%m/%d %H:%M
    if '-' in time_str:
        if (':' in time_str):
            time_fmt = "%Y-%m-%d %H:%M:%S"
        else:
            time_fmt = "%Y-%m-%d"
    else:
        if (':' in time_str):
            time_fmt = "%Y/%m/%d %H:%M"
        else:
            time_fmt = "%Y/%m/%d"
    return int(time.mktime(time.strptime(time_str, time_fmt))) / 3600

def int_to_time(time_int):
    datetime_struct = datetime.datetime.fromtimestamp(time_int * 3600)
    return datetime_struct.strftime('%Y-%m-%d %H:%M')