# Allison Schubauer and Daisy Hernandez
# Created: 6/05/2013
# Last Updated: 6/05/2013
# For JCAP

import numpy as np
from datareader import *
from dictionary_helpers import *
from date_helpers import *

""" does all of the data processing necessary for
    deposition plots """

ROW_BUFFER = []
zndec = 2
tndec = 1

def getDataRow(row):
    global ROW_BUFFER
    if ROW_BUFFER == []:
        ROW_BUFFER += [row]
    else:
        print row
        anglecolnum = getCol('Platen Motor Position')
        print row[anglecolnum]
        angle = round(float(row[anglecolnum]), 0)
        print angle
        radcolnum = getCol('Platen Zshift Motor 1 Position')
        print row[radcolnum]
        radius = round(float(row[radcolnum]), 1)
        print radius
        if (angle == round(float(ROW_BUFFER[-1][anglecolnum]), 0) and radius ==
            round(float(ROW_BUFFER[-1][radcolnum]), 1)):
            ROW_BUFFER += [row]
        else:
            processData(angle, radius)
            ROW_BUFFER = []
    # send to ROW_BUFFER if same azimuth
    # otherwise empty buffer (?) and then add row
    #   call processData() as well

def roundZ(zcol):
    zrnd=np.round(zcol, decimals=zndec)
    for zval in zrnd:
        if zval not in FILE_INFO['Z_mm']:
            zval = -1
    return zrnd

def roundt(tcol):
    trnd=np.round(tcol, decimals=tndec)
    for tval in trnd:
        if tval not in FILE_INFO['TiltDeg']:
            tval = -1
    return trnd

def getRowRange():
    zcolnum = getCol('Platen Zshift Motor 1 Position')
    tcolnum = getCol('Src%d Motor Tilt Position' % int(FILE_INFO['Source']))
    data = np.array(ROW_BUFFER)
    datacols = data.T
    zcol = datacols[zcolnum]
    print 'zcol', zcol
    tcol = datacols[tcolnum]
    print 'tcol', tcol
    inds_useful=np.where((roundZ(zcol)>=0)&
                            (roundt(tcol)>=0))[0]
    return (inds_useful[0], inds_useful[-1])

def getTimeSpan(dataArrayT):
    datecol = getCol('Date')
    timecol = getCol('Time')
    datetimeTup = zip(dataArrayT[datecol], dataArrayT[timecol])
    startStr = datetimeTup[0][0] + ' ' + datetimeTup[0][1]
    endStr = datetimeTup[-1][0] + ' ' + datetimeTup[-1][1]
    durationObj = dateObjFloat(endStr) - dateObjFloat(startStr)
    return durationObj.total_seconds()

def getXtalRate(ratenum, dataArrayT):
    rcolnum = getCol('Xtal%d Rate' % ratenum)
    return np.array(dataArrayT[rcolnum])

def getDepRates(timespan, dataArrayT):
    depRates = []
    for x in range(2,5):
        rateData = getXtalRate(x, dataArrayT)
        rateDiff = rateData[-1] - rateData[0]
        depRates += [rateDiff/timespan]
    
def processData(angle, radius):
    rowRange = getRowRange()
    datacols = np.array(ROW_BUFFER).T
    dataArrayT = datacols[rowRange[0]:(rowRange[1]+1)]
    timespan = getTimeSpan(dataArrayT)
    depRates = getDepRates(timespan, dataArrayT)
    rate0 = getXtalRate(3, dataArrayT).mean()
    rate1 = rate0 * depRates[2]/depRates[1]
    rate2 = rate0 * depRates[0]/depRates[1]
    if radius == FILE_INFO['Z_mm'][0]:
        x = radius * np.cos(angle * np.pi/180.)
        y = radius * np.cos(angle * np.pi/180.)
    else:
        x = radius * np.cos(angle * np.pi/180. + np.pi)
        y = radius * np.cos(angle * np.pi/180. + np.pi)
    rate = np.concatenate([[rate0], rate1, rate2])

