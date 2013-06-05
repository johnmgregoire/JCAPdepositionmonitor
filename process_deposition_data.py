# Allison Schubauer and Daisy Hernandez
# Created: 6/05/2013
# Last Updated: 6/05/2013
# For JCAP

import numpy as np
from datareader import *
from dictionary_helpers import *

""" does all of the data processing necessary for
    deposition plots """

ROW_BUFFER = []
zndec = 2
tndec = 1

def getDataRow(row):
    # send to ROW_BUFFER if same azimuth
    # otherwise empty buffer (?) and then add row
    #   call processData() as well
    pass

def roundZ(zcol):
    zrnd=np.round(zcol, decimals=zndec)
    for zval in zcol:
        if zval not in FILE_INFO['Z_mm']:
            zval = -1
    return zcol

def roundt(tcol):
    trnd=np.round(tcol, decimals=tndec)
    for tval in tcol:
        if tval not in FILE_INFO['TiltDeg']:
            tval = -1
    return tcol

def getRowRange():
    zcolnum = DATA_HEADINGS.getCol('Platen Zshift Motor 1 Position')
    tcolnum = DATA_HEADINGS.getCol('Src%d Motor Tilt Position' % FILE_INFO['Source'])
    data = np.array(ROW_BUFFER)
    datacols = data.T
    zcol = data.T[zcolnum]
    tcol = data.T[tcolnum]
    inds_useful=numpy.where((roundZ(zcol)>=0)&
                            (roundt(tcol)>=0))[0]
    return (inds_useful[0], inds_useful[-1])

def getTimeSpan(rowRange):
    datecol = DATA_HEADINGS.getCol('Date')
    timecol = DATA_HEADINGS.getCol('Time')
    

def getXtalRate(ratenum, rowRange):
    rcolnum = DATA_HEADINGS.getCol('Xtal%d Rate' % ratenum)
    
def processData():
    rowRange = getRowRange()
    timeSpan = getTimeSpan(rowRange)
    
