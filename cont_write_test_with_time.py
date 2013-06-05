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
headers =  [ "Date" , "Time" , "" , "Value" ]

for j in range(additionalCols):
    headers += [ "Value"+str(j) ]

# Empty columns to simulate real files
    headers += [""]
    headers += [""]
    headers += [""]

csvwriter.writerow(headers)

origTime = time.time()

# flush to the file ever "flushTime" seconds
flushTime = 0.1

while num < 1000:
    
    # Date handling
    x = time.time()

    #Getting the MS data
    ms = (str(x).split('.'))[1]
    
    fulldate = strftime("%d/%m/%Y %H:%M:%S", time.localtime(x))
    currentDT = fulldate.split()
    
    # The date in the form dd/mm/yyyy
    date = str(currentDT[0])

    Ttime = currentDT[1]+':'+ms
    # Ttime = currentDT[1]

    # Done in order to slow down the processing
    print Ttime

    content = [ date , Ttime , "", str(num%50)]
    
    for j in range(2,additionalCols+2):
        content += [ str(num % (j*50))]

    content += [""]
    content += [""]
    content += [""]
    

    # Modifiy to simulate writing speed
    time.sleep(0.1)
    csvwriter.writerow(content)

    y = time.time()

    # Flush every second
    if(y - origTime >= flushTime):
    
        origTime = y
        csvfile.flush()
    
    num += 1

csvfile.close()
