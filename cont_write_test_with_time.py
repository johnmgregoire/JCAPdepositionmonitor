# Allison Schubauer and Daisy Hernandez
# Created: 5/21/2013
# Last Updated: 5/23/2013
# For JCAP

import csv
import time
import time
from datetime import datetime
from time import gmtime, strftime
import logging

### Test program for simulating a constantly updating csv file (not infinite)
### This simulates time

testfile = 'testcsv.csv'


csvfile = open(testfile, 'wb')
csvwriter = csv.writer(csvfile)
csvwriter.writerow([ "Date" , "Time" , "Value" , "Value2" , "AValue" ])
num = 0


while num < 1000:
    
    # Date handeling
    x = time.time()

    #Getting the MS data
    ms = (str(x).split('.'))[1]
    
    fulldate = strftime("%x %H:%M:%S", time.localtime(x))
    currentDT = fulldate.split()
    
    # The date in the form mm/dd/yyyy
    date = str(currentDT[0])

    Ttime = currentDT[1]+':'+ms
    # Ttime = currentDT[1]

    # Done in order to slow down the processing
    # print Ttime
    
    csvwriter.writerow([ date , Ttime , str(num%50) , str(num%100) , str(num%200) ])
    
    num += 1

csvfile.close()
