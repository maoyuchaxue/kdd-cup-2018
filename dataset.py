import os
import numpy as np
import csv
import time
import datetime
import math
import win32file

win32file._setmaxstdio(2048)

import utils

class Dataset:
    def __init__(self, aq_path, aq_csv, meo_path, meo_csv, city, split_ratio=(0.8, 0.2), batch_size=50, is_train=True):
        self.aq_path = aq_path
        self.aq_csv = aq_csv
        self.meo_path = meo_path
        self.meo_csv = meo_csv
        self.is_train = is_train
        if is_train:
            self.split_ratio = split_ratio
        else:
            self.split_ratio = (1,)
        self.batch_size = batch_size
        self.data_ind = [0 for i in split_ratio]

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

        self.meo_expanded_dims = self.meo_dim * self.time_steps

        self.init_stations()
        self.load_data()

        # print(self.aq_stations, self.meo_stations)

    def init_stations(self):
        
        aq_csv_file = open(self.aq_csv, "r")
        aq_csv_reader = csv.reader(aq_csv_file)
        self.aq_stations = [] # (station name, x, y)
        for l in aq_csv_reader:
            if (len(l) >= 3):
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
        time_set = None
        
        if (self.is_train):
            self.aq_readers = []
            self.aq_files = []
            for aq_station_info in self.aq_stations:
                tmp_time_set = set()
                aq_station_data = {}
                aq_file_name = os.path.join(self.aq_path, aq_station_info[0] + ".csv")

                # if (len(self.aq_readers) == 0):
                aq_file = open(aq_file_name, "r")
                aq_reader = csv.reader(aq_file)
                for l in aq_reader:
                    if (len(l) == self.aq_input_dims * self.time_steps + 1):
                        cur_time = utils.time_to_int(l[0])
                        tmp_time_set.add(cur_time)

                aq_file.close()
                if (time_set == None):
                    time_set = tmp_time_set
                else:
                    time_set &= tmp_time_set

                cur_aq_files = [open(aq_file_name, "r") for i in range(len(self.split_ratio))]
                cur_aq_readers = [csv.reader(aq_file) for aq_file in cur_aq_files]
                self.aq_readers.append(cur_aq_readers)
                self.aq_files.append(cur_aq_files)
                print(aq_station_info[0])

            # break

        self.meo_readers = []
        self.meo_files = []
        for meo_station_info in self.meo_stations:
            tmp_time_set = set()
            
            meo_file_name = os.path.join(self.meo_path, meo_station_info[0] + ".csv")

            # if (len(self.meo_files) == 0):
            meo_file = open(meo_file_name, "r")
            meo_reader = csv.reader(meo_file)
            for l in meo_reader:
                if (len(l) != self.meo_expanded_dims + 1):
                    continue
                cur_time = utils.time_to_int(l[0])
                tmp_time_set.add(cur_time)
            if (time_set == None):
                time_set = tmp_time_set
            else:
                time_set &= tmp_time_set
            meo_file.close()
            print(meo_station_info[0])

            cur_meo_files = [open(meo_file_name, "r") for i in range(len(self.split_ratio))]
            cur_meo_readers = [csv.reader(meo_file) for meo_file in cur_meo_files]
            self.meo_readers.append(cur_meo_readers)
            self.meo_files.append(cur_meo_files)

        time_list = sorted(list(time_set))
        # jmp_list = []
        # for i in range(len(time_list)-1):
        #     dif = time_list[i+1] - time_list[i]
        #     if (dif != 1):
        #         print(int_to_time(time_list[i]), int_to_time(time_list[i+1]))
        #         jmp_list.append(dif-1)
        # print("total miss:", len(jmp_list), sum(jmp_list))

        self.n = len(time_list)
        self.ns = [int(self.n * ratio) for ratio in self.split_ratio[:-1]]
        self.ns += [self.n - sum(self.ns)]
        print(self.ns)

        self.data_times = [time_list[sum(self.ns[:i]):sum(self.ns[:(i+1)])] for i in range(len(self.split_ratio))]

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
        type_index_dict = {"train":0, "val":1, "test":2}
        t = type_index_dict[batch_type]
        
        start = self.data_ind[t]
        end = self.data_ind[t] + self.batch_size
        if (end > self.ns[t]):
            end = self.ns[t]

        time_slice = self.data_times[t][start:end]

        aq_data_arr = []
        meo_data_arr = []
        # prev_aq_data_arr = []
        for tim in time_slice:
            
            if (self.is_train):
                cur_aq_data_arr = []
                # cur_prev_aq_data_arr = []
                for reader_arr in self.aq_readers:
                    reader = reader_arr[t]
                    l = next(reader)
                    while (len(l) <= self.aq_input_dims * self.time_steps or utils.time_to_int(l[0]) != tim):
                        l = next(reader)
                    l = l[1:]
                    cur_aq_data_arr.append([float(l[i]) for i in self.aq_features_in_file])
                    # cur_prev_aq_data_arr.append([float(i) for i in l[self.prev_aq_features_in_file]])


                aq_data_arr.append(cur_aq_data_arr)
            # prev_aq_data_arr.append(cur_prev_aq_data_arr)

            cur_meo_data_arr = []
            for reader_arr in self.meo_readers:
                reader = reader_arr[t]
                l = next(reader)
                while (len(l) <= 2 or utils.time_to_int(l[0]) != tim):
                    l = next(reader)
                cur_meo_data_arr.append([float(i) for i in l[1:]])
            meo_data_arr.append(cur_meo_data_arr)

        if (end  + self.batch_size > self.ns[t]):
            # this epoch is finished. reopen all files and reset all readers.


            if (self.is_train):
                for f_arr in self.aq_files:
                    f_arr[t].close()

                for stat_ind, aq_station_info in enumerate(self.aq_stations):
                    aq_file_name = os.path.join(self.aq_path, aq_station_info[0] + ".csv")
                    cur_aq_file = open(aq_file_name, "r")
                    cur_aq_reader = csv.reader(cur_aq_file)
                    self.aq_readers[stat_ind][t] = cur_aq_reader
                    self.aq_files[stat_ind][t] = cur_aq_file

            for f_arr in self.meo_files:
                f_arr[t].close()
            
            for stat_ind, meo_station_info in enumerate(self.meo_stations):            
                meo_file_name = os.path.join(self.meo_path, meo_station_info[0] + ".csv")
                cur_meo_file = open(meo_file_name, "r")
                cur_meo_reader = csv.reader(cur_meo_file)
                self.meo_readers[stat_ind][t] = cur_meo_reader
                self.meo_files[stat_ind][t] = cur_meo_file

            self.data_ind[t] = 0

        else:
            self.data_ind[t] = end

        
        if (self.is_train):
            return np.array(aq_data_arr), np.array(meo_data_arr)
        else:
            return np.array(meo_data_arr)
        # return np.array(aq_data_arr), np.array(prev_aq_data_arr), np.array(meo_data_arr)
        

def getDataset(city, time_type="hourunit", split_ratio=(0.8, 0.2), batch_size=50, is_train=True, date=""):
    
    if (is_train):
        path_format_str = "./data/preprocessed/{time_type}/{data_type}_data/{city}"
    else:
        path_format_str = "./data/" + date + "/preprocessed/{time_type}/{data_type}_data/{city}"

    aq_csv_fn = "./data/preprocessed/{city}_aqstation.csv".format(city=city)

    if (city == "london_others" or city == "london_predict" or city == "london"):
        meo_csv_fn = "./data/London_grid_weather_station.csv"
    else:
        meo_csv_fn = "./data/Beijing_grid_weather_station.csv"

    return Dataset(path_format_str.format(city=city, time_type=time_type, data_type="aq"), aq_csv_fn, 
            path_format_str.format(city=city, time_type=time_type, data_type="meo"), meo_csv_fn
            , city, split_ratio, batch_size, is_train)
    

if __name__ == "__main__":
    dataset = getDataset("beijing", "hourunit", batch_size=10, is_train=True)
    dist_mat = dataset.get_dist_matrix()
    x,y = (dataset.get_next_batch())
    print(x.shape,y.shape)



            
    
        
        
