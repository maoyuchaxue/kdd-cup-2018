import csv
import math

days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

## [aqstation, longitude, latitude]
def getAqStation(city):
    aq_station_list = []
    fn = "data/preprocessed/" + city + "_aqstation.csv"
    csv_file = csv.reader(open(fn, 'r'))
    for line in csv_file:
        if len(line) > 0:
            aq_station_list.append([line[0], float(line[1]), float(line[2])])
    return aq_station_list

def getGridList(city):
    if city == "beijing":
        fn = "data/Beijing_grid_weather_station.csv"
    else:
        fn = "data/London_grid_weather_station.csv"
    csv_file = csv.reader(open(fn, 'r'))
    gridlist = []
    for line in csv_file:
        gridid = line[0]
        gridlongitude = line[2]
        gridlatitude = line[1]
        gridlist.append([gridid, gridlongitude, gridlatitude])
    return gridlist

def genMeoPrepocessed(city):
    gridlist = getGridList(city)
    csvfilelist = []
    writerlist = {}

    for grid in gridlist:
        fn = "data/preprocessed/rawdata/" + grid[0] + ".csv"
        csv_file = open(fn, 'w')
        csvfilelist.append(csv_file)
        writerlist[grid[0]] = csv.writer(csv_file)

    if city == "beijing":
        fn = "data/Beijing_historical_meo_grid.csv"
    else:
        fn = "data/London_historical_meo_grid.csv"

    csv_file = csv.reader(open(fn, 'r'))
    isfirstline = True
    for line in csv_file:
        if isfirstline:
            isfirstline = False
        else:
            stationid = line[0]
            time = line[3]
            temperature = float(line[4])
            pressure = float(line[5])
            humidity = float(line[6])
            winddirect = float(line[7])
            windspeed = float(line[8])
            tmpstate = [time, temperature, pressure, humidity, winddirect, windspeed]
            writerlist[stationid].writerow(tmpstate)
    
    for csvfile in csvfilelist:
        csvfile.close()

def calWind(windd1, windd2, winds1, winds2):
    if windd1 == 999017:
        return windd2, winds1 + winds2
    if windd2 == 999017:
        return windd1, winds1 + winds2
    windx1 = winds1 * 1.0 * math.cos(windd1 / 180.0 * math.pi)
    windy1 = winds1 * 1.0 * math.sin(windd1 / 180.0 * math.pi)
    windx2 = winds2 * 1.0 * math.cos(windd2 / 180.0 * math.pi)
    windy2 = winds2 * 1.0 * math.sin(windd2 / 180.0 * math.pi)

    windx = windx1 + windx2
    windy = windy1 + windy2

    winds = math.sqrt(windx ** 2 + windy ** 2)

    if winds < 0.5:
        windd = 999017
    else:
        windd = math.atan(windy * 1.0 / windx) / math.pi * 180
    return windd, winds

# temperature, pressure, humidity, wind_direction, wind_speed/kph
def genListRes(data, l):
    res = [0, 0, 0, 0, 0]
    if len(data) >= l:
        # temperature, pressure and humidity
        for datatype in range(3):
            for index in range(len(data) - l, len(data)):
                res[datatype] = res[datatype] + float(data[index][datatype])
            res[datatype] = res[datatype] * 1.0 / l
        
        # wind_direction and wind_speed
        for index in range(len(data) - l, len(data)):
            res[3], res[4] = calWind(res[3], float(data[index][3]), res[4], float(data[index][4]))   
        res[4] = res[4] * 1.0 / l
        return res
    else:
        return []          


def updatelist(datalist, newdata, timetype):
    res = []
    datalist.append(newdata)
    if timetype == 0:
        timelist = [3, 6, 12, 24]
    else:
        timelist = [1, 3, 7, 14, 30]
    if len(datalist) > timelist[-1]:
        datalist.pop(0)
    for time in timelist:
        tmpres = genListRes(datalist, time)
        res = res + tmpres
    return res

def genEnhancedParsing(gridid):
    readfn = "data/preprocessed/rawdata/" + gridid + ".csv"
    writefn = "data/preprocessed/hourunit/" + gridid + ".csv"
    writefn2 = "data/preprocessed/dayunit/" + gridid + ".csv"
    csv_file = csv.reader(open(readfn, 'r'))
    csv_file2 = csv.writer(open(writefn, 'w'))
    csv_file3 = csv.writer(open(writefn2, 'w'))

    hlist = []
    daylist = []

    for line in csv_file:
        time = line[0]

        res = line
        newdata = line[1:]

        hres = updatelist(hlist, newdata, 0) 
        res = res + hres
        csv_file2.writerow(res)

        if time.find("23:00:00") != -1:
            daydata = hres[15: ]
            res = [time.split(' ')[0]]
            dayres = updatelist(daylist, daydata, 1)    
            csv_file3.writerow(res + dayres)

     
if __name__ == "__main__":
#    genMeoPrepocessed("beijing")
#    genMeoPrepocessed("london")
    gridlist = getGridList("beijing")
    for grid in gridlist:
        genEnhancedParsing(grid[0])
    gridlist = getGridList("london")
    for grid in gridlist:
        genEnhancedParsing(grid[0])