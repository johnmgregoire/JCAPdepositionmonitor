# Allison Schubauer and Daisy Hernandez
# Created: 6/5/2013
# Last Updated: 6/5/2013
# For JCAP

import csv
import time

filename = 'Ag_Src1_Supply1_11W_t20_z3.0_z3.6.csv'
testfile = 'testcsv.csv'

datafile = open(filename, 'rb')
csvfile = open(testfile, 'wb')


csvwriter = csv.writer(csvfile)


linesToWrite = 100
sleepTime = 0.1


x = 0
while x < linesToWrite:

    data = datafile.readline()
    content = data.split(',')
    content[-1]= content[-1][:-2]
    print content
    csvwriter.writerow(content)
    csvfile.flush()
    time.sleep(sleepTime)
    x += 1
    

csvfile.close()
datafile.close()
