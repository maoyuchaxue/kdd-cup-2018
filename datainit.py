import xlrd
import csv

def initAqStation(city):
    aqstation = []
    if city == "beijing":
        workbook = xlrd.open_workbook("data/Beijing_AirQuality_Stations_cn.xlsx")
        booksheet = workbook.sheet_by_name("Sheet1")
        for row in range(booksheet.nrows):
            tmplist = []
            for col in range(booksheet.ncols):
                val = booksheet.cell(row, col).value
                if col == 0:
                    val = str(val.encode("utf-8"))
                    if val.find("aq") != -1:
                        tmplist.append(val) 
                    else:
                        break
                else:
                    val = float(val)
                    tmplist.append(val)
            if len(tmplist) > 0:
                aqstation.append(tmplist)
    return aqstation

def rewriteAqStation(aqstation, city):
    csvFile = open("data/" + city + "_aqstation.csv", "w")
    writer =  csv.writer(csvFile)
    for i in range(len(aqstation)):
        writer.writerow(aqstation[i])
    csvFile.close()

if __name__ == "__main__":
    aqstation = initAqStation("beijing")
    rewriteAqStation(aqstation, "beijing")