from airvisual import genRequest
import csv
import sys

if __name__ == "__main__":
    date = sys.argv[1]
    cnt = 0
    ld_aq_posi = {}
    with open("./data/preprocessed/london_predict_aqstation.csv", "r") as f:
        csv_file = csv.reader(f)
        for line in csv_file:
            if line != "":
                cnt = cnt + 1
                ld_aq_posi[line[0]] = (line[1], line[2])
    
    bj_aq_posi = {}
    with open("./data/preprocessed/beijing_aqstation.csv", "r") as f:
        csv_file = csv.reader(f)
        for line in csv_file:
            if line != "":
                cnt = cnt + 1
                bj_aq_posi[line[0]] = (line[1], line[2])

    aq_station = ""
    aq_data_pm10 = []
    aq_data_pm25 = []
    aq_data_o3 = []
    city = ""
    
    curr = 0

    with open("./data/sample_submission.csv", "r") as f:
        csv_file = csv.reader(f)
        csv_file2 = csv.writer(open("./data/ans/" + date + ".csv", "w"))
        for line in csv_file:
            if line[0] == "test_id":
                csv_file2.writerow(line)
                continue
            index = int(line[0].split("#")[1])
            if line[0].split("#")[0] != aq_station:
                curr = curr + 1
                aq_station = line[0].split("#")[0]
                print str(curr) + " of " + str(cnt) + " : " + aq_station
                if ld_aq_posi.has_key(aq_station):
                    city = "london"
                    lon, lat = ld_aq_posi[aq_station]
                    lon = float(lon)
                    lat = float(lat)
                    aq_data_pm10 = genRequest(lon, lat, date, "london", "pm10")
                    aq_data_pm25 = genRequest(lon, lat, date, "london", "pm25")
                else:
                    city = "beijing"
                    lon, lat = bj_aq_posi[aq_station]
                    lon = float(lon)
                    lat = float(lat)
                    aq_data_pm10 = genRequest(lon, lat, date, "beijing", "pm10")
                    aq_data_pm25 = genRequest(lon, lat, date, "beijing", "pm25")
                    aq_data_o3 = genRequest(lon, lat, date, "beijing", "o3")
            if city == "beijing":
                line[1] = aq_data_pm25[index]
                line[2] = aq_data_pm10[index]
                line[3] = aq_data_o3[index]
            else:
                line[1] = aq_data_pm25[index]
                line[2] = aq_data_pm10[index]
            csv_file2.writerow(line)                                