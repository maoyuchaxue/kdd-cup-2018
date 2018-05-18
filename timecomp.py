def datecomp(time1, time2):
    if time1.find("-") == -1:
        time1 = time1.split("/")
    else:
        time1 = time1.split("-")

    if time2.find("-") == -1:
        time2 = time2.split("/")
    else:
        time2 = time2.split("-")

    sum1 = 0
    sum2 = 0
    for t in range(3):
        sum1 = sum1 * 100 + int(time1[t])
        sum2 = sum2 * 100 + int(time2[t])

    if sum1 > sum2:
        return 0
    if sum1 == sum2:
        return 1
    if sum1 < sum2:
        return 2    

def timecomp(time1, time2):
    time1 = time1.split(":")
    time2 = time2.split(":")

    sum1 = 0
    sum2 = 0
    for t in range(2):
        sum1 = sum1 * 100 + int(time1[t])
        sum2 = sum2 * 100 + int(time2[t])

    if sum1 > sum2:
        return 0
    if sum1 == sum2:
        return 1
    if sum1 < sum2:
        return 2    

