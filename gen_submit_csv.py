
import argparse
import sys, os
import math
import utils
import csv

date = "2018-05-31"

beijing_test_name = "aq"
beijing_inf = 0

london_test_name = "mlpl"
london_inf = 0

outfile_label = "mlp"

os.system("python3 ./aq_mlp_main.py --test --city beijing --inf {inf} --name {name} --date {date}".format(
    inf=beijing_inf, name=beijing_test_name, date=date))

os.system("python3 ./mlp_main.py --test --city london --inf {inf} --name {name} --date {date}".format(
    inf=london_inf, name=london_test_name, date=date))

output_filename_beijing = "./data/output/beijing-{test_date}-{test_name}.out.csv".format(test_date=date, test_name=beijing_test_name)

output_filename_london = "./data/output/london-{test_date}-{test_name}.out.csv".format(test_date=date, test_name=london_test_name)

output_filename_merged = "./data/output/{label}_{test_date}_merged.out.csv".format(test_date=date, label=outfile_label)

def get_predict_stations():
    f1 = open("./data/preprocessed/london_predict_aqstation.csv", "r")
    f2 = open("./data/preprocessed/beijing_aqstation.csv", "r")
    
    lst = []
    for f in [f1, f2]:
        t = csv.reader(f)
        for l in t:
            if (len(l) >= 3):
                lst.append(l[0])
        f.close()
    print(lst)
    return lst

pred_list = get_predict_stations()

station_dict = {}
station_list = []
for fn in [output_filename_beijing, output_filename_london]:
    f = open(fn, "r")
    r = csv.reader(f)    
    for l in r:
        station_name = l[0]
        if (not station_name in pred_list):
            continue

        station_datas = [float(i) for i in l[1:]]
        if not station_name in station_dict:
            station_dict[station_name] = []
            station_list.append(station_name)
        station_dict[station_name].append(station_datas)
    f.close()

f_out = open(output_filename_merged, "w")
f_out.write("test_id,PM2.5,PM10,O3\n")
for name in station_list:
    station_data = station_dict[name]
    for i in range(48):
        row_data = [t if t > 0 else 0 for t in station_data[i]]
        if (len(row_data) == 2):
            row_data.append("")
        f_out.write(name + "#" + str(i) + "," + str(row_data[0]) + "," + str(row_data[1]) + "," + str(row_data[2]) + "\n")
f_out.close()
