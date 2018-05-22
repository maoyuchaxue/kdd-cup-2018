import csv
import numpy as np
from utils import *

def genAqlistPosi(aqlist, aqstation):
    cnt = 0
    for station in aqlist:
        if station[0] == aqstation:
            return cnt
        else:
            cnt = cnt + 1
    return -1

def compData(city, raw_pred_data, date, aq_station_list):
    if city == "beijing":
        actual_data = np.zeros(shape=(48 * 35, 3))
        pred_data = np.zeros(shape=(48 * 35, 3))
    else:
        actual_data = np.zeros(shape=(48 * 13, 2))
        pred_data = np.zeros(shape=(48 * 13, 2))

    isFirst = True
    cnt = 0
    with open("./data/actual/" + date + "-" + city + "-actual.csv", "r") as f:
        csv_file = csv.reader(f)
        for line in csv_file:
            if isFirst:
                isFirst = False
                continue
            station_id = line[1]
            date = line[2].split(" ")[0]
            time_index = int(line[2].split(" ")[1].split(":")[0])
            if date != next_date(date):
                time_index = time_index + 24

            aq_index = genAqlistPosi(aq_station_list, station_id)
            if city == "beijing":
                if line[3] != "" and line[4] != "" and line[7] != "":
                    actual_data[cnt][0] = line[3]
                    actual_data[cnt][1] = line[4]
                    actual_data[cnt][2] = line[7]
                    pred_data[cnt][0] = raw_pred_data[time_index][aq_index * 6]
                    pred_data[cnt][1] = raw_pred_data[time_index][aq_index * 6 + 1]
                    pred_data[cnt][2] = raw_pred_data[time_index][aq_index * 6 + 4]
                    cnt = cnt + 1
            else:
                if line[3] != "" and line[4] != "":
                    actual_data[cnt][0] = line[3]
                    actual_data[cnt][1] = line[4]
                    pred_data[cnt][0] = raw_pred_data[time_index][aq_index * 3]
                    pred_data[cnt][1] = raw_pred_data[time_index][aq_index * 3 + 1]
                    cnt = cnt + 1
    return SMAPE(actual_data[0 : cnt, :], pred_data[0 : cnt, :])