import csv

## [aqstation, longitude, altitude, stationtype]
def getAqStation(city):
    aq_station_list = []
    if city == "beijing":
        fn = "data/beijing_aq_station.csv"
    csv_file = csv.reader(open(fn, 'r'))
    for line in csv_file:
        if len(line) > 0:
            aq_station_list.append([line[0], float(line[1]), float(line[2])])
    return aq_station_list


aq_station =  getAqStation("beijing")
for station in aq_station:
    print station
