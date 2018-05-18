import numpy as np
import csv
import utils
from sklearn.preprocessing import Imputer

class SequencedAQData:
    def __init__(self, city, aq_csv_fn, meo_csv_fn, need_scale=False):
        self.need_scale = need_scale

        self.seq_data = {} # 48 * stations * aq_features
        self.city = city

        self.step_list = [3, 6, 12, 24]
        if (self.city == "beijing"):        
            self.aq_cols = [0, 1, 4]
            self.aq_input_dims = 6
        else:
            self.aq_cols = [0, 1]
            self.aq_input_dims = 6

        if (need_scale):
            tmp_aq_means, tmp_aq_scales = utils.get_scale_params(city, "aq")
            self.aq_means = {k:[] for k in tmp_aq_means.keys()}
            self.aq_scales = {k:[] for k in tmp_aq_scales.keys()}
            tk = list(tmp_aq_means.keys())[0]
            for i in range(len(tmp_aq_means[tk])):
                if ((i % self.aq_input_dims) in self.aq_cols and i >= self.aq_input_dims):
                    for k in tmp_aq_means.keys():
                        self.aq_means[k].append(tmp_aq_means[k][i])
                        self.aq_scales[k].append(tmp_aq_scales[k][i])
        
        self.aq_csv = aq_csv_fn
        self.meo_csv = meo_csv_fn

        self.init_stations()

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
    
    def add_row(self, aq_data_row):
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
        res_data = np.reshape(res_data, (1, self.stations, self.aq_features * len(self.step_list))) # stations * aq_features * timesteps
        
        if (self.need_scale):
            means = np.zeros(res_data.shape)
            scales = np.zeros(res_data.shape)
            for i, station_info in enumerate(self.aq_stations):
                means[0, i, :] = np.array(self.aq_means[station_info[0]])
                scales[0, i, :] = np.array(self.aq_scales[station_info[0]])
            res_data = (res_data - means) / scales

        return res_data

    def reverse_scale(self, pred):
    
        if (self.need_scale):
            new_pred = np.zeros(pred.shape)

            for i, station_info in enumerate(self.aq_stations):
                cur_station = station_info[0]
                for t in range(1):
                    cur_means, cur_scales = self.aq_means[cur_station], self.aq_scales[cur_station]
                    new_pred[t, i, :] = [pred[t, i, d] * cur_scales[d] + cur_means[d] for d in range(pred.shape[2])]
                    
            return new_pred
        else:
            return pred
        
    
    def load_from_csvs(self, csvs):
        self.station_names = []

        min_t = None
        for fn in csvs:
            f = open(fn, "r")
            r = csv.reader(f)
                
            for l in r:
                if (len(l) == 0):
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

        for t in range(int(min_t), int(min_t)+48):
            t_arr = []
            for station_info in self.aq_stations:
                station = station_info[0]
                if (not station in self.seq_data):
                    t_arr.append([np.nan for i in range(len(self.aq_cols))])
                    # t_arr.append([0 for i in range(len(self.aq_cols))])
                elif (not t in self.seq_data[station]):
                    t_arr.append([np.nan for i in range(len(self.aq_cols))])
                else:
                    t_arr.append(self.seq_data[station][t])
            seq_arr.append(t_arr)

        self.seq_data = np.array(seq_arr)
        print(self.seq_data.shape)
        self.times, self.stations, self.aq_features = self.seq_data.shape

        print(self.seq_data[0])
        self.seq_data = np.reshape(self.seq_data, (self.times * self.stations, -1))
        print(self.seq_data.shape)
        imp = Imputer(strategy='mean', axis=0)
        imp.fit(self.seq_data)
        print(self.seq_data.shape)
        self.seq_data = imp.transform(self.seq_data)
        print(self.seq_data.shape)
        self.seq_data = np.reshape(self.seq_data, (self.times, self.stations, self.aq_features))

def getSequencedAQDataForDate(city, date, need_scale=False):

    aq_csv_fn = "./data/preprocessed/{city}_aqstation.csv".format(city=city)

    if (city == "london_others" or city == "london_predict" or city == "london"):
        meo_csv_fn = "./data/London_grid_weather_station.csv"
    else:
        meo_csv_fn = "./data/Beijing_grid_weather_station.csv"

    seq = SequencedAQData(city, aq_csv_fn, meo_csv_fn, need_scale=need_scale)
    
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