import os

for i in range(1, 14):
    cmd = "python ./grab_data.py 2018-05-" + str(i).zfill(2)
    print(cmd)
    os.system(cmd)