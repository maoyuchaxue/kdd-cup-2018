import requests
import re

def parseApiText(t):
    pattern = re.compile("\[0\]\[0\], (\d+\.\d+)")
    data = pattern.findall(t)
    data = [data[0]] + data
    return map(lambda x: float(x), data)

#    lon, lat = 0.070766, 51.45258 #116.417, 39.929 #-0.1258, 51.522
#    date = '2018-05-21'

def genRequest(lon, lat, date, city, predict_type):
    # http://silam.fmi.fi/thredds/dodsC/silam_europe_v5_5_1/runs/silam_europe_v5_5_1_RUN_2018-04-27T00:00:00Z.ascii?cnc_PM2_5[0:3:71][0:1:0][205:5:225][230:5:270]
    #http://silam.fmi.fi/thredds/dodsC/daily_silam_china_v5_5_1/runs/daily_silam_china_v5_5_1_RUN_2018-04-29T00:00:00Z.ascii?daymax_cnc_PM2_5[0:1:0][0:1:0][0:1:0][0:1:0]
    bj_pre_pm10 = 'http://silam.fmi.fi/thredds/dodsC/silam_china_v5_5_1/runs/silam_china_v5_5_1_RUN_{}T00:00:00Z.ascii?cnc_PM10'
    ld_pre_pm10 = 'http://silam.fmi.fi/thredds/dodsC/silam_europe_v5_5_1/runs/silam_europe_v5_5_1_RUN_{}T00:00:00Z.ascii?cnc_PM10'
    bj_pre_pm25 = 'http://silam.fmi.fi/thredds/dodsC/silam_china_v5_5_1/runs/silam_china_v5_5_1_RUN_{}T00:00:00Z.ascii?cnc_PM2_5'
    ld_pre_pm25 = 'http://silam.fmi.fi/thredds/dodsC/silam_europe_v5_5_1/runs/silam_europe_v5_5_1_RUN_{}T00:00:00Z.ascii?cnc_PM2_5'
    bj_pre_o3 = 'http://silam.fmi.fi/thredds/dodsC/silam_china_v5_5_1/runs/silam_china_v5_5_1_RUN_{}T00:00:00Z.ascii?cnc_O3_gas'
    # ex)BL0-London
    # Actual [lon,lat]
    # SILAM Grid Map(230,205) corresponds to 'london_grid_000'(-2,50.5)
    def map_ld(lon, lat):
        gplon = 10 #699/(44.95000076293945+24.950000762939453)
        gplat = 10 #419/(71.94999694824219 - 30.049999237060547)
        x, y = int((lon - (-24.950000762939453)) * gplon), int((lat - (30.049999237060547)) * gplat)
        return x, y
    def map_bj(lon, lat):
        gplon = 8 #638/(146.875-67.125)
        gplat = 8 #374/(53.875-7.125)
        x, y = int((lon - 67.125) * gplon), int((lat - 7.125) * gplat)
        return x, y
    
    if city == "beijing":
        x, y = map_bj(lon, lat)
    else:
        x, y = map_ld(lon, lat)
    print(x, y)

    if city == "beijing":
        if predict_type == "pm10":
            prefix = bj_pre_pm10.format(date)
        elif predict_type == "pm25":
            prefix = bj_pre_pm25.format(date)
        elif predict_type == "o3":
            prefix = bj_pre_o3.format(date)
    else:
        if predict_type == "pm10":
            prefix = ld_pre_pm10.format(date)
        elif predict_type == "pm25":
            prefix = ld_pre_pm25.format(date)
    time = '[0:1:46]'
    height = '[0:1:0]'
    lat_range = '[' + str(y) + ':1:' + str(y) + ']'
    lon_range = '[' + str(x) + ':1:' + str(x) + ']'
    url = prefix + time + height + lat_range + lon_range
    r = requests.get(url)
#    print(url)
#    print(r.text)
    return  parseApiText(r.text)
