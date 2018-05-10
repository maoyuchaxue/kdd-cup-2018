import csv
import os

fnprefix = "./data/preprocessed/dayunit/meo_data/"
fnprefix2 = "./data/preprocessed/hourunit/meo_data/"
fnprefix3 = "./data/preprocessed/splitdata/"

def genSplitDir(city, date):
    os.mkdir()

def genSplitData(city, gridnum, is_day):
    if is_day:
        csv_file = csv.reader(open(fnprefix + city + "/" + gridnum + ".csv", "r"))
    else:
        csv_file = csv.reader(open(fnprefix2 + city + "/" + gridnum + ".csv", "r"))

    data_date = ""
    for line in csv_file:
        tmp_date = line[0].split(" ")[0]
        if not is_day:
            tmp_time = line[0].split(" ")[1]
        if data_date != tmp_date:
            p = fnprefix3 + city + "/" + tmp_date
            if not os.path.exists(p):
                os.mkdir(p)
            if is_day:
                csv_file2 = csv.writer(open(p + "/daydata.csv", "a"))
            else:
                csv_file2 = csv.writer(open(p + "/hourdata.csv", "a"))
        data_date = tmp_date
        if is_day:
            csv_file2.writerow([gridnum] + line[1:])
        else:
            csv_file2.writerow([gridnum, tmp_time] + line[1:])

if __name__ == "__main__":
    city = "beijing"
    for i in range(0, 651):
        gridnum = "beijing_grid_" + str(i).zfill(3)
        print gridnum
        genSplitData(city, gridnum, True)
        genSplitData(city, gridnum, False)
    city = "london"
    for i in range(0, 861):
        print gridnum
        gridnum = "london_grid_" + str(i).zfill(3)
        genSplitData(city, gridnum, True)
        genSplitData(city, gridnum, False)  
