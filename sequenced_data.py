import numpy as np
import csv
import utils
from sklearn.preprocessing import Imputer

class SequencedAQData:
    def __init__(self, city):
        self.seq_data = {} # 48 * stations * aq_features
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

        res_data = np.concatenate(concat_data, axis=2)
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

                station_name = l[0]
                if (not station_name in self.seq_data):
                    self.seq_data[station_name] = {}
                    self.station_names.append(station_name)
                t = utils.time_to_int(l[1])
                if (min_t == None or t < min_t):
                    min_t = t

                # print(time_offset)
                cur_data_strs = [l[i+2] for i in self.aq_cols]
                cur_data = [float(s) if len(s)>0 else np.nan for s in cur_data_strs]
                self.seq_data[station_name][t] = cur_data
        
        seq_arr = []

        for t in range(min_t, min_t+48):
            t_arr = []
            for station in self.station_names:
                if (not t in self.seq_data[station]):
                    t_arr.append([np.nan for i in range(len(self.aq_cols))])
                else:
                    t_arr.append(self.seq_data[station][t])
            seq_arr.append(t_arr)

        self.seq_data = np.array(seq_arr)
        print(self.seq_data.shape)
        self.times, self.stations, self.aq_features = self.seq_data.shape

        self.seq_data = np.reshape(self.seq_data, (self.times * self.stations, -1))
        imp = Imputer(strategy='mean', axis=0)

        imp.fit(self.seq_data)
        self.seq_data = imp.transform(self.seq_data)
        print(self.seq_data.shape)
        self.seq_data = np.reshape(self.seq_data, (self.times, self.stations, self.aq_features))

def getSequencedAQDataForDate(city, date):

    seq = SequencedAQData(city)
    
    date_prev1 = utils.prev_date(date)
    date_prev2 = utils.prev_date(date_prev1)
    print(date_prev2, date_prev1)

    path_format = "./data/preprocessed/splitdata/{city}/{date}/aq.csv"
    seq.load_from_csvs([path_format.format(date=date_prev2, city=city), path_format.format(date=date_prev1, city=city)])
    return seq

if (__name__ == "__main__"):
    seq = getSequencedAQDataForDate("beijing", "2018-05-13")
    p = seq.get_next_average_info()
    print(p.shape)