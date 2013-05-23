# Allison Schubauer and Daisy Hernandez
# Created: 5/21/2013
# Last Updated: 5/21/2013
# For JCAP

import csv
import time
import time
from time import gmtime, strftime
import logging

### Test program for simulating a constantly updating csv file (not infinite)
### This simulates time

testfile = 'testcsv.csv'

csvfile = open(testfile, 'wb')
csvwriter = csv.writer(csvfile)
csvwriter.writerow([ "Date" , "Time" , "Value" ])
num = 0 
while num < 10000:
    fulldate = strftime("%x %H:%M:%S", gmtime())
    microSec = str(time.time()).split('.')
    currentDT = fulldate.split()
    date = str(currentDT[0])
    Ttime = currentDT[1]+'.'+microSec[-1]
    csvwriter.writerow([ date , Ttime , str(num%50) ])
    num += 1

csvfile.close()
