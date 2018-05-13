import numpy as np
import csv

class SequencedAQData:
    def __init__(self, city, seq_len):
        self.seq_data = {} # 48 * stations * aq_features
        self.seq_len = seq_len
        self.city = city

        self.step_list = [3, 6, 12, 24]
        if (self.city == "beijing"):        
            self.aq_cols = [0, 1, 4]
        else:
            self.aq_cols = [0, 1]
    
    def add_row(self, time, aq_data_row):
        self.seq_data = self.seq_data[1:,:,:]
        aq_data = aq_data_row.reshape((1, self.stations, self.aq_features)) 
        self.seq_data = np.concatenate([self.seq_data, aq_data], axis=0)

    def get_next_average_info(self):
        concat_data = []
        for step in self.step_list:
            t_data = self.seq_data[-step:,:,:]
            mean_data = np.mean(t_data, axis=0) # mean along time axis
            mean_data = mean_data.reshape((self.stations, self.aq_features, 1))
            concat_data.append(mean_data)

        res_data = np.concat(concat_data, axis=2)
        return res_data # stations * aq_features * timesteps
    
    def load_from_csvs(self, csvs):
        self.station_names = []

        min_t = None
        for fn in csvs:
            f = open(fn, "r")
            r = csv.reader(f)
                
            first = True
            for l in r:
                if first:
                    first = False
                    continue

                station_name = l[1]
                if (not station_name in self.seq_data):
                    self.seq_data[station_name] = {}
                    self.station_names.append(station_name)
                t = utils.time_to_int(l[2])
                if (min_t == None or t < min_t):
                    min_t = t

                # print(time_offset)
                cur_data = [float(l[i+3]) for i in aq_cols]
                self.seq_data[station_name][t] = cur_data
        
        seq_arr = []

        for t in range(min_t, min_t+48):
            t_arr = []
            for station in self.station_names:
                t_arr.append(self.seq_data[station][t])
            seq_arr.append(t)

        self.seq_data = np.array(seq_arr)
        
        print(self.seq_data.shape)
        self.times, self.stations, self.aq_features = self.seq_data.shape