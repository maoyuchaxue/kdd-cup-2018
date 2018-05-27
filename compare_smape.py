import csv
import utils
import numpy as np

fn_pred = "./data/output/london-2018-05-17-mlpl.out.csv"
fn_actual = "./data/output/05-17-london-actual.csv"
city = "ld"

if (city == "bj"):
    aq_cols = [0, 1, 4]
else:
    aq_cols = [0, 1]

fpred = open(fn_pred, "r")
rp = csv.reader(fpred)

station_dict = {}
station_list = []

for l in rp:
    station_name = l[0]
    station_datas = [float(i) for i in l[1:]]
    
    if not station_name in station_dict:
        station_dict[station_name] = []
        station_list.append(station_name)

    station_dict[station_name].append(station_datas)

factual = open(fn_actual, "r")
ra = csv.reader(factual)

real_data = []
pred_data = []

min_t = None
first = True
for l in ra:
    if first:
        first = False
        continue

    complete = True
    if (city == "bj"):
        for z in l:
            if (len(z) == 0):
                complete = False
                break
    else:
        for z in l[:-3]:
            if (len(z) == 0):
                complete = False
                break
    if (not complete):
        continue

    station_name = l[1]
    t = utils.time_to_int(l[2])
    if ((not min_t) or t < min_t):
        min_t = t
    time_offset = (t - min_t)
    # print(time_offset)
    cur_data = [float(l[i+3]) for i in aq_cols]

    real_data.append(cur_data)
    pred_data.append(station_dict[station_name][time_offset])

real_data = np.array(real_data)
pred_data = np.array(pred_data)

print(real_data.shape, pred_data.shape)
print(utils.SMAPE(real_data, pred_data))

