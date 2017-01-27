import csv

f1 = file('testdata.csv', 'r')


c1 = csv.reader(f1)

totalcount = 0

for hosts_row in c1:
    print(hosts_row)

f1.close()
