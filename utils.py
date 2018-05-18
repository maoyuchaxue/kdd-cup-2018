import numpy as np
import math
import time
import os
import csv
import datetime
from sklearn import preprocessing

# eps = 1e-4

def SMAPE(actual, predicted):
    # p = pred
    predicted[predicted < 0] = 0
    # return np.mean(np.abs(actual - p) / ((actual + p + eps) / 2.0))
    dividend= np.abs(np.array(actual) - np.array(predicted))
    denominator = np.array(actual) + np.array(predicted)
    return 2 * np.mean(np.divide(dividend, denominator, out=np.zeros_like(dividend), where=denominator!=0, casting='unsafe'))


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

def next_date(date):
    datetime_next = int_to_time(time_to_int(date) + 24)
    return datetime_next.split(" ")[0]

def prev_date(date):
    datetime_next = int_to_time(time_to_int(date) - 24)
    return datetime_next.split(" ")[0]

def gen_dist_matrix(aq_stations, meo_stations):
    dist_dim = 6
    dist_mat = []
    for aq_station_info in aq_stations:
        dist_row = []
        aq_x = aq_station_info[1]
        aq_y = aq_station_info[2]

        for meo_station_info in meo_stations:
            meo_x = meo_station_info[1]
            meo_y = meo_station_info[2]
            dist = math.sqrt((meo_x-aq_x)**2 + (meo_y-aq_y)**2)
            dist_row.append([dist, 1.0/dist, 1.0/(dist*1.5), 1.0/(dist*2), 1.0/(dist*3), 1.0/(dist*4)])
        dist_mat.append(dist_row)

    dist_matrix = np.array(dist_mat)
    dist_matrix /= dist_matrix.shape[1]

    original_shape = dist_matrix.shape

    dist_matrix = np.reshape(dist_matrix, (-1, dist_dim))
    dist_matrix = preprocessing.scale(dist_matrix, axis=0)
    dist_matrix = np.reshape(dist_matrix, original_shape)

    return dist_dim, dist_matrix

    
def get_scale_params(city, data_type="aq", time_type="hourunit"):
    means = {}
    scales = {}
    params_path = "./data/preprocessed/{time_type}/{data_type}_data/{city}/".format(city=city, data_type=data_type, time_type=time_type)

    for fn in os.listdir(params_path):
        if (fn.endswith("_params.csv")):
            station_id = fn.replace("_params.csv", "")
            full_fn = os.path.join(params_path, fn)
            reader = csv.reader(open(full_fn, "r"))

            first = True
            for l in reader:
                if (len(l) == 0):
                    continue

                if (first):
                    first = False
                    means[station_id] = [float(i) for i in l]
                else:
                    scales[station_id] = [float(i) for i in l]

    print(len(means), len(scales))
    return means, scales
