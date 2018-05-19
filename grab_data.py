import urllib2
import csv
from dataparser import calWind, updatelist
from dataparser import genListRes
import os
import sys
import utils
from sklearn import preprocessing

urlprefix = "https://biendata.com/competition/meteorology/"
urlprefix2 = "http://kdd.caiyunapp.com/competition/forecast/"
url_aq_format = "https://biendata.com/competition/airquality/{city_short}/{date}-0/{date}-23/2k0d1d8"

global lastday
global lasthr

lasthr = []
lastday = []
# tmpstate = [time, temperature, pressure, humidity, winddirect, windspeed]

should_redownload = False;


def getAQData(city, date):
    if city == "beijing":
        city_short = "bj"
    else:
        city_short = "ld"
    url = url_aq_format.format(city_short=city_short, date=date)
    print(url)

    save_path = "./data/preprocessed/splitdata/{city}/{date}".format(date=date, city=city)
    save_fn = os.path.join(save_path, "aq.csv")

    if (not os.path.exists(save_path)):
        os.mkdir(save_path)
    if (os.path.exists(save_fn) and os.path.getsize(save_fn) > 100):
        print("existed")
        if (not should_redownload):
            return

    f = urllib2.urlopen(url)
    lastline = []
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
            csv_writer.writerow(tmpline[1:])
    
    

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
        if (not should_redownload):
            return

    f = urllib2.urlopen(url)
    lastline = []
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
            if len(tmpline) == 9:
                csv_writer.writerow(tmpline[1:3] + tmpline[4:])
                lastline = tmpline[4:]
            else:
                csv_writer.writerow(tmpline[1:3] + lastline)

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
        if (not should_redownload):
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
            if len(tmpline) == 9:
                csv_writer.writerow(tmpline[1:3] + tmpline[4:7] + [tmpline[8], tmpline[7]])
                lastline = tmpline[4:7] + [tmpline[8], tmpline[7]]
            else:
                csv_writer.writerow(tmpline[1:3] + lastline)

# change id,station_id,time,weather,temperature,pressure,humidity,wind_speed,wind_direction
# into station_id, time,temperature,pressure,humidity,wind_direction,wind_speed
def parseData(city, raw_dates, date, day1, day2):
    global lastday
    global lasthr
    
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
            if len(line) != 7:
                if len(lasthr) != 0:
                    newdata = lasthr
                else:
                    newdata = ["16", "990", "35", "0", "0"]
            else:
                newdata = line[2:]
                lasthr = newdata

            hres = updatelist(hlist[gridid], newdata, 0, 0) 
            res = res + hres
            if tmpday == day1 or tmpday == day2:
                csv_file2.writerow(res)

            if time.find("23:00:00") != -1:
                if len(hlist[gridid]) < 24:
                    if len(lastday) != 0:
                        daydata = lastday
                    else:
                        daydata = ["16", "990", "35", "0", "0"]
                else:
                    daydata = hres[15: ]
                    lastday = daydata
                dayres = updatelist(daylist[gridid], daydata, 1, 0)    
                if tmpday == day1 or tmpday == day2:
                    csv_file3.writerow([gridid] + [time.split(' ')[0]] + dayres)

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
    dates = [utils.int_to_time(cur_t - 24 * i) for i in range(4)]
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

    for city in ["beijing", "london"]:
        prev_date = utils.prev_date(today)
        prev_date2 = utils.prev_date(prev_date)
        getAQData(city, prev_date)
        getAQData(city, prev_date2)