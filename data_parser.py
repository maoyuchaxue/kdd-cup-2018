import csv
import utils
import math
import numpy as np
import sklearn.preprocessing as pre


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

    data_dict = {}
    for grid in gridlist:
        data_dict[grid[0]] = []

    if city == "beijing":
        fn = "data/Beijing_historical_meo_grid.csv"
    else:
        fn = "data/London_historical_meo_grid.csv"

    csv_file = csv.reader(open(fn, 'r'))
    isfirstline = True

    cnt = 0
    for line in csv_file:
        if isfirstline:
            isfirstline = False
        else:
            cnt += 1
            if (cnt % 10000 == 0):
                print cnt
            stationid = line[0]
            time = line[3]
            temperature = float(line[4])
            pressure = float(line[5])
            humidity = float(line[6])
            winddirect = float(line[7])
            windspeed = float(line[8])
            tmpstate = [time, temperature, pressure, humidity, winddirect, windspeed]
            data_dict[stationid].append(tmpstate)
            # writerlist[stationid].writerow(tmpstate)
    
    for grid in gridlist:
        fn = "data/preprocessed/rawdata/meo_data/" + city + "/" + grid[0] + ".csv"
        csv_file = open(fn, 'w')  
        writer = csv.writer(csv_file)
        for row in data_dict[grid[0]]:        
            writer.writerow(row)
        csv_file.close()

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
        windd = 180
    else:
        windd = math.atan(windy * 1.0 / windx) / math.pi * 180
        if windd < 0:
            windd = windd + 360
    return windd, winds

# temperature, pressure, humidity, wind_direction, wind_speed/kph
def genListRes(data, l, datakind):
    if l != 1 and datakind != 0:
        offset = -1
    else:
        offset = 0
    if len(data) + offset >= l:
        # meo data
        if datakind == 0:
            res = [0, 0, 0, 0, 0]
            # temperature, pressure and humidity
            for datatype in range(3):
                for index in range(len(data) - l, len(data)):
                    try:
                        res[datatype] = res[datatype] + float(data[index][datatype])
                    except IndexError:
                        print data
                        print data[index]
                        print index, datatype
                res[datatype] = res[datatype] * 1.0 / l
            
            # wind_direction and wind_speed
            for index in range(len(data) - l, len(data)):
                res[3], res[4] = calWind(res[3], float(data[index][3]), res[4], float(data[index][4]))   
            res[4] = res[4] * 1.0 / l

            for i in range(len(res)):
                res[i] = round(res[i], 4)
            return res
        else:
            # aqdata
            res = []
            for i in range(datakind):
                res.append(0)
            for datatype in range(datakind):
                for index in range(len(data) - l + offset, len(data) + offset):
                    res[datatype] = res[datatype] + float(data[index][datatype])
                res[datatype] = res[datatype] * 1.0 / l
            for i in range(len(res)):
                res[i] = round(res[i], 4)
            return res
    else:
        return []          


def updatelist(datalist, newdata, timetype, datatype):
    res = []
    datalist.append(newdata)
    if timetype == 0:
        timelist = [3, 6, 12, 24]
    else:
        timelist = [1, 3, 7, 14, 30]
    if len(datalist) > timelist[-1] + 1:
        datalist.pop(0)
    for time in timelist:
        tmpres = genListRes(datalist, time, datatype)
        res = res + tmpres
    return res

def genEnhancedParsing(city, gridid):
    readfn = "data/preprocessed/rawdata/meo_data/" + city + "/" + gridid + ".csv"
    writefn = "data/preprocessed/hourunit/meo_data/" + city + "/" + gridid + ".csv"
    writefn_params = "data/preprocessed/hourunit/meo_data/" + city + "/" + gridid + "_params.csv"
    writefn2 = "data/preprocessed/dayunit/meo_data/" + city + "/" + gridid + ".csv"
    writefn2_params = "data/preprocessed/dayunit/meo_data/" + city + "/" + gridid + "_params.csv"

    csv_file = csv.reader(open(readfn, 'r'))
    csv_file2 = csv.writer(open(writefn, 'w'))
    csv_file2_params = csv.writer(open(writefn_params, 'w'))

    csv_file3 = csv.writer(open(writefn2, 'w'))
    csv_file3_params = csv.writer(open(writefn2_params, 'w'))

    hlist = []
    daylist = []

    hour_res_arr = []
    hour_time_list = []
    day_res_arr = []
    day_time_list = []

    for line in csv_file:
        time = line[0]

        res = line
        newdata = line[1:]

        hres = updatelist(hlist, newdata, 0, 0) 
        res = newdata + hres

        if (len(res) >= 25):
            hour_res_arr.append(res)
            hour_time_list.append(time)

        if time.find("23:00:00") != -1:
            daydata = hres[15: ]
            cur_time = time.split(' ')[0]
            dayres = updatelist(daylist, daydata, 1, 0)    
            res = dayres
            if (len(res) >= 25):
                day_res_arr.append(res)
                day_time_list.append(cur_time)

    hour_res = np.array(hour_res_arr)
    hour_scaler = pre.StandardScaler()
    hour_scaler.fit(hour_res)
    hour_res = hour_scaler.transform(hour_res)

    csv_file2_params.writerow([m for m in hour_scaler.mean_])
    csv_file2_params.writerow([m for m in hour_scaler.scale_])
    for i in range(hour_res.shape[0]):
        csv_file2.writerow([hour_time_list[i]] + [round(m, 4) for m in hour_res[i]])

    day_res = np.array(day_res_arr)
    day_scaler = pre.StandardScaler()
    day_scaler.fit(day_res)
    day_res = day_scaler.transform(day_res)
    csv_file3_params.writerow([m for m in day_scaler.mean_])
    csv_file3_params.writerow([m for m in day_scaler.scale_])

    for i in range(day_res.shape[0]):
        csv_file3.writerow([day_time_list[i]] + [round(m, 4) for m in day_res[i]])
    print(hour_res.shape, day_res.shape)
    
## aq
# london pm2.5 pm10 no2
# beijing PM2.5,PM10,NO2,CO,O3,SO2
def genAqEnhancedParsing(city, stationid):
    readfn = "data/preprocessed/rawdata/aq_data/" + city + "/" + stationid + ".csv"
    writefn = "data/preprocessed/hourunit/aq_data/" + city + "/" + stationid + ".csv"
    writefn_params = "data/preprocessed/hourunit/aq_data/" + city + "/" + stationid + "_params.csv"
    writefn2 = "data/preprocessed/dayunit/aq_data/" + city + "/" + stationid + ".csv"
    writefn2_params = "data/preprocessed/dayunit/aq_data/" + city + "/" + stationid + "_params.csv"
    csv_file = csv.reader(open(readfn, 'r'))
    csv_file2 = csv.writer(open(writefn, 'w'))
    csv_file2_params = csv.writer(open(writefn_params, 'w'))

    csv_file3 = csv.writer(open(writefn2, 'w'))
    csv_file3_params = csv.writer(open(writefn2_params, 'w'))

    if city == "beijing":
        datakind = 6
    else:
        datakind = 3

    hlist = []
    daylist = []

    hour_res_arr = []
    hour_time_list = []
    day_res_arr = []
    day_time_list = []

    for line in csv_file:
        time = line[0]

        res = line
        newdata = line[1:]

        hres = updatelist(hlist, newdata, 0, datakind) 
        res = newdata + hres

        if len(hres) == datakind * 4:
            hour_res_arr.append(res)
            hour_time_list.append(time)

        if time.find("23:00") != -1 and len(hres) == datakind * 4:
            daydata = hres[datakind * 3: ]
            cur_time = time.split(' ')[0]
            dayres = updatelist(daylist, daydata, 1, datakind)    
            
            res = dayres
            if (len(res) >= datakind * 5):
                day_res_arr.append(res)
                day_time_list.append(cur_time)


    hour_res = np.array(hour_res_arr)
    hour_scaler = pre.StandardScaler()
    hour_scaler.fit(hour_res)
    hour_res = hour_scaler.transform(hour_res)

    csv_file2_params.writerow([m for m in hour_scaler.mean_])
    csv_file2_params.writerow([m for m in hour_scaler.scale_])
    for i in range(hour_res.shape[0]):
        csv_file2.writerow([hour_time_list[i]] + [round(m, 4) for m in hour_res[i]])

    day_res = np.array(day_res_arr)
    day_scaler = pre.StandardScaler()
    day_scaler.fit(day_res)
    day_res = day_scaler.transform(day_res)
    csv_file3_params.writerow([m for m in day_scaler.mean_])
    csv_file3_params.writerow([m for m in day_scaler.scale_])

    for i in range(day_res.shape[0]):
        csv_file3.writerow([day_time_list[i]] + [round(m, 4) for m in day_res[i]])
    print(hour_res.shape, day_res.shape)
    

def rewriteAqRawData(datalist, vallist, valcnt, city, stationid, gval, gcnt, a):
    print stationid 
    fn = "data/preprocessed/rawdata/aq_data/" + city + "/" + stationid + ".csv"
    if a:
        csv_file = open(fn, 'a')
    else:
        csv_file = open(fn, 'w')
    csv_writer = csv.writer(csv_file)

    for data in datalist:
        for i in range(1, len(data)):
            if data[i] == "":
                if valcnt[i - 1] == 0:
                    data[i] = round(gval[i - 1] * 1.0 / gcnt[i - 1], 4)
                else:
                    data[i] = round(vallist[i - 1] * 1.0 / valcnt[i - 1], 4)
        csv_writer.writerow(data)
    for i in range(len(vallist)):
        vallist[i] = 0
        valcnt[i] = 0
    csv_file.close()

def genRawAqData(city, isforecast, a):
    if city == "beijing":
        if a:
            fn = "data/beijing_201802_201803_aq.csv"
        else:
            fn = "data/beijing_17_18_aq.csv"
        stationindex = 0
        dataindex = 2
        tmpval = [0, 0, 0, 0, 0, 0]
        valcnt = [0, 0, 0, 0, 0, 0]
        gval = [0, 0, 0, 0, 0, 0]
        gcnt = [0, 0, 0, 0, 0, 0]
        datalen = 8
    if city == "london":
        if isforecast:
            fn = "data/London_historical_aqi_forecast_stations_20180331.csv"
            stationindex = 2
            dataindex = 3
            datalen = 6
        else:
            fn = "data/London_historical_aqi_other_stations_20180331.csv"
            stationindex = 0
            dataindex = 2
            datalen = 5
        tmpval = [0, 0, 0]
        valcnt = [0, 0, 0]
        gval = [0, 0, 0]
        gcnt = [0, 0, 0]

    csv_file = csv.reader(open(fn, 'r'))        
    is_firstline = True
    tmpstation = ""
    timeindex = 1
    tmplist = []
    for line in csv_file:
        if is_firstline:
            is_firstline = False
        else:
            if tmpstation != line[stationindex]:
                if tmpstation != "":
                    for i in range(len(tmpval)):
                        gval[i] = gval[i] + tmpval[i]
                        gcnt[i] = gcnt[i] + valcnt[i]
                    rewriteAqRawData(tmplist, tmpval, valcnt, city, tmpstation, gval, gcnt, a)
                tmplist = []
            tmpstation = line[stationindex]
            tmplist.append([line[timeindex]] + line[dataindex: datalen])
            for i in range(dataindex, datalen):
                if line[i] != "":
                    valcnt[i - dataindex] = valcnt[i - dataindex] + 1
                    tmpval[i - dataindex] = tmpval[i - dataindex] + float(line[i])

    if tmpstation != "":    
        for i in range(len(tmpval)):
            gval[i] = gval[i] + tmpval[i]
            gcnt[i] = gcnt[i] + valcnt[i]
        rewriteAqRawData(tmplist, tmpval, valcnt, city, tmpstation, gval, gcnt, a)
    
if __name__ == "__main__":
    
    # genMeoPrepocessed("beijing")
    # genMeoPrepocessed("london")


    gridlist = getGridList("beijing")
    for grid in gridlist:
        print(grid[0])
        genEnhancedParsing("beijing", grid[0])
        
    gridlist = getGridList("london")
    for grid in gridlist:
        print(grid[0])
        genEnhancedParsing("london", grid[0])
    
    
    # genRawAqData("beijing", True, False)
    # genRawAqData("beijing", True, True)
    # genRawAqData("london", False, False)
    # genRawAqData("london", True, False)
    
    aqstation = getAqStation("beijing")
    for station in aqstation:
        print station[0]
        genAqEnhancedParsing("beijing", station[0])

    aqstation = getAqStation("london_predict")
    for station in aqstation:
        print station[0]
        genAqEnhancedParsing("london", station[0])

    aqstation = getAqStation("london_others")
    for station in aqstation:
        print station[0]
        genAqEnhancedParsing("london", station[0])
