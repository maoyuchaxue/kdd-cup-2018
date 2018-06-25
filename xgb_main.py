# -*- coding:utf-8 -*-

import xgboost as xgb
from xgb_model import DataSet
import numpy as np
import csv
from parse_actual_data import compData
import sys
reload(sys)
sys.setdefaultencoding('utf8')

abspath = "/Users/junxianshen/Documents/本学期课程/数据挖掘/kddcup/code"

# setup parameters for xgboost
param = {}
# scale weight of positive examples
param['eta'] = 0.4
param['max_depth'] = 10
param['silent'] = 1

def genAqlistPosi(aqlist, aqstation):
    cnt = 0
    for station in aqlist:
        if station[0] == aqstation:
            return cnt
        else:
            cnt = cnt + 1
    return -1

def saveSubmission(beijing_predict, london_predict, beijing_aqstation, london_aqstation, date):
    isFirst = True
    with open(abspath + "/data/sample_submission.csv", "r") as f:
        csv_file = csv.reader(f)
        csv_file2 = csv.writer(open(abspath + "/data/ans/" + date + ".csv", "w"))
        for line in csv_file:
            if isFirst:
                isFirst = False
                csv_file2.writerow(line)
                continue
            station_id = line[0].split("#")[0]
            station_index = int(line[0].split("#")[1])
            bj_aq_index = genAqlistPosi(beijing_aqstation, station_id)
            ld_aq_index = genAqlistPosi(london_aqstation, station_id)
            if bj_aq_index != -1:
                line[1] = beijing_predict[station_index][bj_aq_index * 6]
                line[2] = beijing_predict[station_index][bj_aq_index * 6 + 1]
                line[3] = beijing_predict[station_index][bj_aq_index * 6 + 4]
            else:
                line[1] = london_predict[station_index][ld_aq_index * 3]
                line[2] = london_predict[station_index][ld_aq_index * 3 + 1]

            csv_file2.writerow(line)

def trainModel():
    num_round = 5

    dataset = DataSet("beijing", True)
    dataset.trainEntrance()
    for i in range(35 * dataset.aq_num):
        print "generating model: " + str(i) + "  of " + str(35 * dataset.aq_num)
        xg_train = xgb.DMatrix(dataset.model, label=dataset.label[:, i : i + 1])
        bst = xgb.train(param, xg_train, num_round)
        bst.save_model(abspath + "/xgb_model/beijing_xgb" + str(i) + ".model")

    dataset = DataSet("london", True)
    dataset.trainEntrance()
    for i in range(13 * dataset.aq_num):
        print "generating model: " + str(i) + "  of " + str(35 * dataset.aq_num)
        xg_train = xgb.DMatrix(dataset.model, label=dataset.label[:, i : i + 1])
        bst = xgb.train(param, xg_train, num_round)
        bst.save_model(abspath + "/xgb_model/london_xgb" + str(i) + ".model")

def genPredict(date):
    dataset = DataSet("london", True)
    dataset.testEntrance(date)
    london_test = xgb.DMatrix(dataset.test)
    london_aqstation = dataset.aq_station

    london_predict = np.array([])
    for i in range(13 * dataset.aq_num):
        print "predicting model: " + str(i) + "  of " + str(13 * dataset.aq_num)
        bst = xgb.Booster(param)
        bst.load_model(abspath + "/xgb_model/london_xgb" + str(i) + ".model")
        if london_predict.shape[0] == 0:
            london_predict = bst.predict(london_test).reshape((48,1))
        else:
            london_predict = np.concatenate((london_predict, bst.predict(london_test).reshape(48,1)), axis=1)

    dataset = DataSet("beijing", True)
    dataset.testEntrance(date)
    beijing_test = xgb.DMatrix(dataset.test)
    beijing_aqstation = dataset.aq_station

    beijing_predict = np.array([])
    for i in range(35 * dataset.aq_num):
        print "predicting model: " + str(i) + "  of " + str(35 * dataset.aq_num)
        bst = xgb.Booster(param)
        bst.load_model(abspath + "/xgb_model/beijing_xgb" + str(i) + ".model")
        if beijing_predict.shape[0] == 0:
            beijing_predict = bst.predict(beijing_test).reshape((48,1))
        else:
            beijing_predict = np.concatenate((beijing_predict, bst.predict(beijing_test).reshape(48,1)), axis=1)

    return beijing_aqstation, london_aqstation, beijing_predict, london_predict

if __name__ == "__main__":
    date = sys.argv[1]

#    trainModel()

    beijing_aqstation, london_aqstation, beijing_predict, london_predict = genPredict(date)

    saveSubmission(beijing_predict, london_predict, beijing_aqstation, london_aqstation, date)

#    print compData("beijing", beijing_predict, date, beijing_aqstation)
#    print compData("london", london_predict, date, london_aqstation)

