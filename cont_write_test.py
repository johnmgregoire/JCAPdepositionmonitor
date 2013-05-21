# Allison Schubauer and Daisy Hernandez
# Created: 5/21/2013
# Last Updated: 5/21/2013
# For JCAP

import csv

### Test program for simulating a constantly updating csv file (not infinite)

testfile = 'testcsv.csv'
csvfile = open(testfile, 'wb')
csvwriter = csv.writer(csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
num = 0 
while num < 10000:
    csvwriter.writerow(str(num))
    num += 1

csvfile.close()
