import urllib2
import csv
from dataparser import calWind, updatelist
from dataparser import genListRes
import os
import sys
import utils

urlprefix = "https://biendata.com/competition/meteorology/"
urlprefix2 = "http://kdd.caiyunapp.com/competition/forecast/"


# tmpstate = [time, temperature, pressure, humidity, winddirect, windspeed]


def getRawPrevData(city, date):
    if city == "beijing":
        grid = "bj_grid/"
    else:
        grid = "ld_grid/"
    url = urlprefix + grid + date + "-0" + "/" + date + "-23" + "/2k0d1d8"
    print(url)

    save_path = "./data/preprocessed/splitdata/{city}/{date}".format(date=date, city=city)
    save_fn = os.path.join(save_path, "raw.csv")
    if (not os.path.exists(save_path)):
        os.mkdir(save_path)
    if (os.path.exists(save_fn) and os.path.getsize(save_fn) > 100):
        print("existed")
        return

    f = urllib2.urlopen(url)
    with open(save_fn, "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        content = f.read().split("\r\n")
        isFirst = True
        for line in content:
            if line == "":
                break
            if isFirst:
                isFirst = False
                continue
            tmpline = line.split(",")
            csv_writer.writerow(tmpline[1:3] + tmpline[4:])

def getForeData(city, date):
    if city == "beijing":
        ct = "bj"
    else:
        ct = "ld"
    url = urlprefix2 + ct + "/" + date + "-23/2k0d1d8"

    save_path = "./data/preprocessed/splitdata/{city}/{date}".format(date=date, city=city)
    save_fn = os.path.join(save_path, "forecast.csv")

    if (not os.path.exists(save_path)):
        os.mkdir(save_path)
    if (os.path.exists(save_fn) and os.path.getsize(save_fn) > 100):
        print("existed")
        return

    f = urllib2.urlopen(url)
    with open(save_fn, "w") as csv_file:
        csv_writer = csv.writer(csv_file)
        content = f.read().split("\r\n")
        isFirst = True
        for line in content:
            if line == "":
                break
            if isFirst:
                isFirst = False
                continue
            tmpline = line.split(",")
            csv_writer.writerow(tmpline[1:3] + tmpline[4:7] + [tmpline[8], tmpline[7]])

# change id,station_id,time,weather,temperature,pressure,humidity,wind_speed,wind_direction
# into station_id, time,temperature,pressure,humidity,wind_direction,wind_speed
def parseData(city, raw_dates, date, day1, day2):
    
    fdir = "./data/preprocessed/splitdata/" + city + "/" + date + "/"
    if not os.path.exists(fdir):
        os.mkdir(fdir)

    csvs = []
    for raw_date in raw_dates:
        save_path = "./data/preprocessed/splitdata/" + city + "/" + raw_date + "/"
        raw_fn = os.path.join(save_path, "raw.csv")
        csvs.append(raw_fn)
    
    forecast_fn = os.path.join(fdir, "forecast.csv")
    csvs.append(forecast_fn)

    csv_file2 = csv.writer(open(fdir + "hourunit.csv", "w"))
    csv_file3 = csv.writer(open(fdir + "dayunit.csv", "w"))
    hlist = {}
    daylist = {}

    if city == "beijing":
        gridnum = 651
    else:
        gridnum = 861
    for i in range(gridnum):
        gridid = city + "_grid_" + str(i).zfill(3)
        hlist[gridid] = []
        daylist[gridid] = []

    for csv_fn in csvs:
        print(csv_fn)
        csv_file = csv.reader(open(csv_fn, 'r'))
        for line in csv_file:
            gridid = line[0]
            time = line[1]

            tmpday = time.split(' ')[0]

            res = line
            newdata = line[2:]

            hres = updatelist(hlist[gridid], newdata, 0, 0) 
            res = res + hres
            if tmpday == day1 or tmpday == day2:
                csv_file2.writerow(res)

            if time.find("23:00:00") != -1:
                daydata = hres[15: ]
                res = [time.split(' ')[0]]
                dayres = updatelist(daylist[gridid], daydata, 1, 0)    
                if tmpday == day1 or tmpday == day2:
                    csv_file3.writerow(res + dayres)

def genNextDay(date):
    date = date.split("-")
    day = date[2]
    tmpday = int(day) + 1
    if tmpday == 32:
        day = "01"
    else:
        day = str(tmpday).zfill(2)
    return date[0] + "-" + date[1] + "-" + day

def genRawDates(date):
    cur_t = utils.time_to_int(date)
    dates = [utils.int_to_time(cur_t - 24 * i) for i in range(31)]
    return [d.split(" ")[0] for d in dates][::-1]

if __name__ == "__main__":
    today = sys.argv[1]
    # print(today)

    tomorrow = genNextDay(today)
    day_after_tomorrow = genNextDay(tomorrow)
    raw_dates = genRawDates(today)

    for d in raw_dates:
        getRawPrevData("london", d)

    getForeData("london", today)
    parseData("london", raw_dates, today, tomorrow, day_after_tomorrow)

    for d in raw_dates:
        getRawPrevData("beijing", d)

    getForeData("beijing", today)
    parseData("beijing", raw_dates, today, tomorrow, day_after_tomorrow)