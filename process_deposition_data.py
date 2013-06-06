# Allison Schubauer and Daisy Hernandez
# Created: 6/05/2013
# Last Updated: 6/06/2013
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
radius1 = 28.
radius2 = 45.

# make sure to make one last call to processData when file finishes

def getDataRow(row):
    global ROW_BUFFER
    if ROW_BUFFER == []:
        ROW_BUFFER += [row]
    else:
        anglecolnum = getCol('Platen Motor Position')
        angle = round(float(row[anglecolnum]))
        # print 'angle:', angle
        zcolnum = getCol('Platen Zshift Motor 1 Position')
        zval = round(float(row[zcolnum]), 1)
        #print 'radius:', radius
        prevangle = round(float(ROW_BUFFER[-1][anglecolnum]), 0)
        prevz = round(float(ROW_BUFFER[-1][zcolnum]), 1)
        if (angle == prevangle and zval == prevz):
            ROW_BUFFER += [row]
        elif (angle == prevangle):
            # make new graph
            print 'drawing new graph for z =', zval
            processData(prevangle, radius1)
            processData(prevangle, radius2)
            ROW_BUFFER = [row]
        else:
            processData(prevangle, radius1)
            processData(prevangle, radius2)
            ROW_BUFFER = [row]

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
    zcol = map(float, datacols[zcolnum])
    tcol = map(float, datacols[tcolnum])
    inds_useful=np.where((roundZ(zcol)>=0)&
                            (roundt(tcol)>=0))[0]
    return (inds_useful[0], inds_useful[-1])

def getTimeSpan(dataArrayT):
    datecol = getCol('Date')
    timecol = getCol('Time')
    # error: array index out of range
    datetimeTup = zip(dataArrayT[datecol], dataArrayT[timecol])
    startStr = datetimeTup[0][0] + ' ' + datetimeTup[0][1]
    endStr = datetimeTup[-1][0] + ' ' + datetimeTup[-1][1]
    durationObj = dateObjFloat(endStr) - dateObjFloat(startStr)
    return durationObj.total_seconds()

def getXtalRate(ratenum, dataArrayT):
    rcolnum = getCol('Xtal%d Rate' % ratenum)
    return np.array(map(float, dataArrayT[rcolnum]))

def getDepRates(timespan, dataArrayT):
    depRates = []
    for x in range(2,5):
        rateData = getXtalRate(x, dataArrayT)
        rateDiff = rateData[-1] - rateData[0]
        depRates += [rateDiff/timespan]
    return depRates
    
def processData(angle, radius):
    rowRange = getRowRange()
    #print 't:', FILE_INFO.get('TiltDeg')
    #print 'rowRange:', rowRange
    if rowRange[0] == rowRange[1]:
        pass
    else:
        #print 'ROW_BUFFER', ROW_BUFFER
        dataArray = ROW_BUFFER[rowRange[0]:(rowRange[1]+1)]
        dataArrayT = np.array(dataArray).T
        #print 'dataArrayT', dataArrayT
        timespan = getTimeSpan(dataArrayT)
        depRates = getDepRates(timespan, dataArrayT)
        rate0 = getXtalRate(3, dataArrayT).mean()
        #Xtal3Rate = map(float, DATA_DICT.get('Xtal3 Rate'))
        #rate0 = np.array(Xtal3Rate).mean()
        rate = rate0
        if radius == radius1:
            if angle == 0:
                #plot rate0 at (0, 0)
                print 'plotting rate0 at (0,0)'
            x = radius * np.cos(angle * np.pi/180.)
            y = radius * np.sin(angle * np.pi/180.)
            # rate1 corresponds to Xtal4 Rate
            rate = rate0 * depRates[2]/depRates[1]
        else:
            x = radius * np.cos(angle * np.pi/180. + np.pi)
            y = radius * np.sin(angle * np.pi/180. + np.pi)
            # rate2 corresponds to Xtal2 Rate
            rate = rate0 * depRates[0]/depRates[1]
        print (angle, radius, x, y, rate)
        # return the tuple above to depgraph
