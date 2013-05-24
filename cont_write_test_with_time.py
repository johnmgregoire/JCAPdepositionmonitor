# Allison Schubauer and Daisy Hernandez
# Created: 5/21/2013
# Last Updated: 5/24/2013
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

num = 0
additionalCols = 20

csvfile = open(testfile, 'wb')
csvwriter = csv.writer(csvfile)
headers =  [ "Date" , "Time" , "Value" ]

for j in range(additionalCols):
    headers += [ "Value"+str(j) ]

csvwriter.writerow(headers)

origTime = time.time()

while num < 100:
    
    # Date handling
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
    print Ttime

    content = [ date , Ttime , str(num%50)]
    
    for j in range(2,additionalCols+2):
        content += [ str(num % (j*50))]

    # Modifiy to simulate writing speed
    time.sleep(0.5)
    csvwriter.writerow(content)

    y = time.time()

    # Flush every second
    if(y - origTime >= 1):
    
        origTime = y
        csvfile.flush()
    
    num += 1

csvfile.close()
