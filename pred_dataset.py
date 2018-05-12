import os
import numpy as np
import csv
import time
import datetime
import math

import utils

class PredDataset:
    def __init__(self, meo_path, aq_csv, meo_csv, city, batch_size=50):
        self.meo_path = meo_path
        self.meo_csv = meo_csv
        self.aq_csv = aq_csv
        self.batch_size = batch_size

        if (city == "beijing"):
            self.aq_dim = 3
            self.aq_input_dims = 6
            self.aq_features_in_file = [0, 1, 4]
        else:
            self.aq_dim = 2
            self.aq_input_dims = 3
            self.aq_features_in_file = [0, 1]

        self.meo_dim = 5
        self.time_steps = 5
        # self.aq_expanded_dims = self.aq_dim * (self.time_steps - 1)
        self.meo_expanded_dims = self.meo_dim * self.time_steps

        self.data_ind = 0
        self.init_stations()
        self.load_data()
        # print(self.aq_stations, self.meo_stations)
        
    def init_stations(self):
        
        aq_csv_file = open(self.aq_csv, "r")
        aq_csv_reader = csv.reader(aq_csv_file)
        self.aq_stations = [] # (station name, x, y)
        for l in aq_csv_reader:
            if (len(l) == 3):
                self.aq_stations.append([l[0], float(l[1]), float(l[2])])
        aq_csv_file.close()

        meo_csv_file = open(self.meo_csv, "r")
        meo_csv_reader = csv.reader(meo_csv_file)
        self.meo_stations = [] # (station name, x, y)
        for l in meo_csv_reader:
            if (len(l) == 3):
                self.meo_stations.append([l[0], float(l[1]), float(l[2])])
        meo_csv_file.close()
        print(len(self.aq_stations), len(self.meo_stations))


    def load_data(self):

        meo_file = open(self.meo_path, "r")
        meo_reader = csv.reader(meo_file)

        station_name_to_index = {info[0]:i for (i, info) in enumerate(self.meo_stations)}

        data_set = {}

        for l in meo_reader:
            if (len(l) != self.meo_expanded_dims + 2):
                continue
            cur_time = utils.time_to_int(l[1])
            cur_station = l[0]
            cur_data = [float(i) for i in l[2:]]
            if (not cur_time in data_set):
                data_set[cur_time] = [None for i in range(len(self.meo_stations))]
            data_set[cur_time][station_name_to_index[cur_station]] = cur_data

        time_list = sorted(data_set.keys())
        
        self.pred_data = []

        for t in time_list:
            time_unit_data = data_set[t]
            time_unit_arr = []
            for i in range(len(self.meo_stations)):
                time_unit_arr.append(time_unit_data[i]) 
            self.pred_data.append(time_unit_arr)
        
        self.pred_data = np.array(self.pred_data)
        self.n = self.pred_data.shape[0]
        print(self.pred_data.shape)

    def get_dist_matrix(self):
        self.dist_dims = 4

        dist_mat = []
        for aq_station_info in self.aq_stations:
            dist_row = []
            aq_x = aq_station_info[1]
            aq_y = aq_station_info[2]

            for meo_station_info in self.meo_stations:
                meo_x = meo_station_info[1]
                meo_y = meo_station_info[2]
                dist = math.sqrt((meo_x-aq_x)**2 + (meo_y-aq_y)**2)
                dist_row.append([dist, 1.0, 1.0/dist, 1.0/(dist*2)])
            dist_mat.append(dist_row)

        self.dist_matrix = np.array(dist_mat)
        self.dist_matrix /= self.dist_matrix.shape[1]
        print("dist matrix shape:", self.dist_matrix.shape)
        return self.dist_matrix

    def get_next_batch(self, batch_type="train"):
        start = self.data_ind
        end = self.data_ind + self.batch_size
        if (end > self.n):
            end = self.n
        return self.pred_data[start:end]

def getPredDataset(city, time_type="hourunit", batch_size=50, date="2018-05-02"):
    
    filename = "./data/preprocessed/splitdata/{city}/{date}/{time_type}.csv".format(city=city, time_type=time_type, date=date)
    
    aq_csv_fn = "./data/preprocessed/{city}_aqstation.csv".format(city=city)
    if (city == "london_others" or city == "london_predict" or city == "london"):
        meo_csv_fn = "./data/London_grid_weather_station.csv"
    else:
        meo_csv_fn = "./data/Beijing_grid_weather_station.csv"
    return PredDataset(filename, aq_csv_fn, meo_csv_fn, city, batch_size)

if __name__ == "__main__":
    dataset = getPredDataset("beijing", "hourunit", batch_size=48)
    dist_mat = dataset.get_dist_matrix()
    x  = (dataset.get_next_batch())
    print(x.shape)



            
    
        
        
