import urllib2
import csv
from dataparser import calWind, updatelist
from dataparser import genListRes
import os


urlprefix = "https://biendata.com/competition/meteorology/"
urlprefix2 = "http://kdd.caiyunapp.com/competition/forecast/"


# tmpstate = [time, temperature, pressure, humidity, winddirect, windspeed]


def getRawPrevData(city, datebegin, dateend):
    if city == "beijing":
        grid = "bj_grid/"
    else:
        grid = "ld_grid/"
    url = urlprefix + grid + datebegin + "/" + dateend + "/2k0d1d8"
    f = urllib2.urlopen(url)
    with open("tmp.csv", "w") as csv_file:
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
    url = urlprefix2 + ct + "/" + date + "/2k0d1d8"
    f = urllib2.urlopen(url)
    with open("tmp.csv", "a") as csv_file:
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
def parseData(city, date, day1, day2):
    csv_file = csv.reader(open("tmp.csv", 'r'))
    fdir = "./data/preprocessed/splitdata/" + city + "/" + date + "/"
    if not os.path.exists(fdir):
        os.mkdir(fdir)
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

def genGetRawDate(date):
    enddate = date + "-23"
    date = date.split("-")
    startdate = date[0] + "-" + str(int(date[1]) - 1).zfill(2) + "-" + date[2] + "-0"
    return startdate, enddate

if __name__ == "__main__":
    today = "2018-04-02"

    tomorrow = genNextDay(today)
    day_after_tomorrow = genNextDay(tomorrow)
    startdate, enddate = genGetRawDate(today)

    getRawPrevData("beijing", startdate, enddate)
    getForeData("beijing", enddate)
    parseData("beijing", today, tomorrow, day_after_tomorrow)
