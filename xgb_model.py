import numpy as np
import csv
import math
from utils import *

class DataSet:
    def __init__(self, city = "beijing", isTrain = True):
        self.city = city
        self.isTrain = isTrain
        self.aq_station = []
        meo_station_list = []

        if city == "beijing":
            self.aq_num = 6
        else:
            self.aq_num = 3

        if city == "beijing":
            self.num_aq_station = 35
            with open("./data/preprocessed/beijing_aqstation.csv", "r") as f:
                csv_reader = csv.reader(f)
                for line in csv_reader:
                    self.aq_station.append(line)
            with open("./data/Beijing_grid_weather_station.csv", "r") as f:
                csv_reader = csv.reader(f)
                for line in csv_reader:
                    meo_station_list.append([line[0], line[2], line[1]])
            
        else:
            # 13 predict, 11 others
            self.num_aq_station = 13 + 11
            with open("./data/preprocessed/london_predict_aqstation.csv", "r") as f:
                csv_reader = csv.reader(f)
                for line in csv_reader:
                    self.aq_station.append(line)
            with open("./data/preprocessed/london_others_aqstation.csv", "r") as f:
                csv_reader = csv.reader(f)
                for line in csv_reader:
                    if line[0] != "CT2":
                        self.aq_station.append(line)
            with open("./data/London_grid_weather_station.csv", "r") as f:
                csv_reader = csv.reader(f)
                for line in csv_reader:
                    meo_station_list.append([line[0], line[2], line[1]])

        self.genMeoStationList(meo_station_list)

    def genMeoStationList(self, meo_station_list):
        self.meo_station = []
        for aq_station in self.aq_station:
            cnt = 0
            for meo_station in meo_station_list:
                if abs(float(meo_station[1]) - float(aq_station[1])) <= 0.10001 and \
                    abs(float(meo_station[2]) - float(aq_station[2])) <= 0.10001:
                    self.meo_station.append(meo_station[0])
                    cnt = cnt + 1
            if cnt < 4:
                print "error"

    def initTrainMatrix(self, row):
        self.row = row
        self.col = len(self.meo_station) * 50
        self.model = np.zeros(shape=(row, self.col))
        self.label = np.zeros(shape=(row, len(self.aq_station) * self.aq_num))


    def initTestMatrix(self):
        self.col = len(self.meo_station) * 50
        self.test = np.zeros(shape=(48, self.col))

    def genTimeList(self, isMeo):
        if isMeo:
            datakind = "meo_data"
            firststation = self.city + "_grid_000.csv"
        else:
            datakind = "aq_data"
            firststation = self.aq_station[0][0] + ".csv"

        first_day = ""
        fn = "./data/preprocessed/dayunit/" + datakind + "/" + self.city + "/" + firststation
        with open(fn) as f:
            csv_file = csv.reader(f)
            for line in csv_file:
                if len(line) == 26:
                    first_day = line[0]
                    break

        print firststation
        self.timelist = []
        isStart = False
        fn = "./data/preprocessed/hourunit/" + datakind + "/" + self.city + "/" + firststation
        with open(fn) as f:
            csv_file = csv.reader(f)
            for line in csv_file:
                if len(line) == 26 and line[0].split(" ")[0] != "2018-03-27" \
                    and line[0].split(" ")[0] != "2018/3/27":
                    if not isStart:
                        if line[0].split(" ")[0] == first_day:
                            isStart = True
                        else:
                            continue
                    self.timelist.append(line[0])

    def trainEntrance(self):
        self.genTimeList(True)
        self.initTrainMatrix(len(self.timelist))
        cnt = 0
        for station in self.meo_station:
            print "generating meo:  " + str(cnt + 1) + "of " + str(len(self.meo_station))
            self.genDataSet(station, cnt)
            cnt = cnt + 1

        cnt = 0
        for station in self.aq_station:
            print "generating aq: " + station[0] + " " + str(cnt + 1) + " of " + str(len(self.aq_station))
            self.genDataSetLabel(station[0], cnt)
            cnt = cnt + 1

    def genDataSet(self, gridid, cnt):
        fn = "./data/preprocessed/hourunit/meo_data/" + self.city + "/" + gridid + ".csv"
        with open(fn, "r") as f:
            csv_file = csv.reader(f)
            list_index = 0
            for line in csv_file:
                if self.timelist[list_index] != line[0]:
                    continue
                else:
                    self.model[list_index][cnt * 50 : cnt * 50 + 25] = \
                        map(lambda x : float(x), line[1:])
                    list_index = list_index + 1
                    if list_index == len(self.timelist):
                        break
        if list_index != len(self.timelist):
            print "somewhere wrong"  
            print list_index  

        fn = "./data/preprocessed/dayunit/meo_data/" + self.city + "/" + gridid + ".csv"
        with open(fn, "r") as f:
            csv_file = csv.reader(f)
            list_index = 0
            for line in csv_file:
                if self.timelist[list_index].split(" ")[0] != line[0]:
                    continue
                else:
                    while list_index < len(self.timelist) and \
                        self.timelist[list_index].split(" ")[0] == line[0]:
                        self.model[list_index][cnt * 50 + 25 : cnt * 50 + 50] = \
                            map(lambda x : float(x), line[1:])
                        list_index = list_index + 1
                    if list_index == len(self.timelist):
                        break
        if list_index != len(self.timelist):
            print "somewhere wrong" 
            while list_index != len(self.timelist):
                print self.timelist[list_index]
                list_index = list_index + 1

    def genDataSetLabel(self, aqid, cnt):
        fn = "./data/preprocessed/hourunit/aq_data/" + self.city + "/" + aqid + ".csv"
        with open(fn, "r") as f:
            csv_file = csv.reader(f)
            list_index = 0
            for line in csv_file:
                
                if time_to_int(line[0]) < time_to_int(self.timelist[list_index]):
                    continue
                elif time_to_int(line[0]) == time_to_int(self.timelist[list_index]):
                    self.label[list_index][cnt * self.aq_num : (cnt + 1) * self.aq_num] = \
                        map(lambda x : float(x), line[1 : 1 + self.aq_num])
                    list_index = list_index + 1  
                    if list_index == len(self.timelist):
                        break
                elif time_to_int(line[0]) > time_to_int(self.timelist[list_index]):
                    while time_to_int(line[0]) > time_to_int(self.timelist[list_index]):
                        self.label[list_index][cnt * self.aq_num : (cnt + 1) * self.aq_num] = \
                            self.label[list_index - 1][cnt * self.aq_num : (cnt + 1) * self.aq_num]
                        list_index = list_index + 1
                        if list_index == len(self.timelist):
                            break
                    if time_to_int(line[0]) == time_to_int(self.timelist[list_index]):
                        self.label[list_index][cnt * self.aq_num : (cnt + 1) * self.aq_num] = \
                            map(lambda x : float(x), line[1 : 1 + self.aq_num])
                        list_index = list_index + 1  
                        if list_index == len(self.timelist):
                            break
        if list_index != len(self.timelist):
            print "somewhere wrong" 
            print self.timelist[list_index]
            '''
            while list_index != len(self.timelist):
                print self.timelist[list_index]
                list_index = list_index + 1
            '''
    
    def testEntrance(self, date):
        self.initTestMatrix()
        cnt = 0
        for station in self.meo_station:
            self.genTestDataSet(station, cnt, date)
            cnt = cnt + 1

    def genTestDataSet(self, gridid, cnt, date):
        fn = "./data/preprocessed/splitdata/" + self.city + "/" + date + "/hourunit.csv"
        list_index = 0
        with open(fn, "r") as f:
            csv_file = csv.reader(f)
            for line in csv_file:
                if line[0] != gridid:
                    continue
                else:
                    self.test[list_index][cnt * 50 : cnt * 50 + 25] = \
                        map(lambda x : float(x), line[2:])
                    list_index = list_index + 1

        fn = "./data/preprocessed/splitdata/" + self.city + "/" + date + "/dayunit.csv"
        list_index = 0
        with open(fn, "r") as f:
            csv_file = csv.reader(f)
            for line in csv_file:
                if line[0] != gridid:
                    continue
                else:
                    for i in range(24):
                        self.test[list_index][cnt * 50 + 25 : cnt * 50 + 50] = \
                            map(lambda x : float(x), line[2:])
                        list_index = list_index + 1
