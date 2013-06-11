# Allison Schubauer and Daisy Hernandez
# Created: 6/05/2013
# Last Updated: 6/07/2013
# For JCAP

import numpy as np
from dictionary_helpers import *
from date_helpers import *
from datareader import *

DEP_DATA = []

""" does all of the data processing necessary for
    deposition plots """

ROW_BUFFER = []
zndec = 2
tndec = 1
radius1 = 28.
radius2 = 45.

class ProcessorThread(QtCore.QThread):
    
    lineRead = QtCore.pyqtSignal(list)
    newData = QtCore.pyqtSignal(list)
    
    def __init__(self, parent=None, filename='default.csv'):
        super(ProcessorThread, self).__init__()
        self.file = filename
        self.changeZ = False
        self.running = True
        self.reader = DataReader(parent=self, filename=self.file)
        self.reader.lineRead.connect(self.newLineRead)

    def run(self):
        self.reader.start()
        while self.running:
            pass

    def newLineRead(self, newRow):
        self.lineRead.emit(newRow)
        self.processRow(newRow)

    def processRow(self, row):
        global ROW_BUFFER
        if ROW_BUFFER == []:
            ROW_BUFFER += [row]
        else:
            anglecolnum = getCol('Platen Motor Position')
            angle = round(float(row[anglecolnum]))
            zcolnum = getCol('Platen Zshift Motor 1 Position')
            zval = round(float(row[zcolnum]), 1)
            prevangle = round(float(ROW_BUFFER[-1][anglecolnum]), 0)
            prevz = round(float(ROW_BUFFER[-1][zcolnum]), 1)
            if (angle == prevangle and zval == prevz):
                ROW_BUFFER += [row]
            elif (angle == prevangle):
                # make new graph
                print 'drawing new graph for z =', zval
                newpt1 = self.processData(prevz, prevangle, radius1)
                newpt2 = self.processData(prevz, prevangle, radius2)
                self.changeZ = True
                ROW_BUFFER = [row]
                if (newpt1 != None and newpt2 != None):
                    self.newData.emit([newpt1, newpt2])
            else:
                newpt1 = self.processData(zval, prevangle, radius1)
                newpt2 = self.processData(zval, prevangle, radius2)
                ROW_BUFFER = [row]
                if (newpt1 != None and newpt2 != None):
                    self.newData.emit([newpt1, newpt2])

    def processData(self, z, angle, radius):
        global DEP_DATA
        rowRange = getRowRange()
        #print 't:', FILE_INFO.get('TiltDeg')
        #print 'rowRange:', rowRange
        if rowRange[1] - rowRange[0] <= 2:
            pass
        else:
            #print 'ROW_BUFFER', ROW_BUFFER
            dataArray = ROW_BUFFER[rowRange[0]:(rowRange[1]+1)]
            dataArrayT = np.array(dataArray).T
            #print 'dataArrayT', dataArrayT
            timespan = getTimeSpan(dataArrayT)
            depRates = getDepRates(timespan, dataArrayT)
            rate0 = getXtalRate(3, dataArrayT).mean()
            #rate0 = np.array(Xtal3Rate).mean()
            rate = rate0
            if radius == radius1:
                if angle == 0 or self.changeZ:
                    #plot rate0 at (0, 0)
                    print 'plotting rate0 at (0,0)'
                    DEP_DATA.append((z, 0.0, 0.0, rate))
                    self.newData.emit([(z, 0.0, 0.0, rate)])
                    self.changeZ = False
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
            DEP_DATA.append((z, x, y, rate))
            # return the tuple above to depgraph
            return (z, x, y, rate)

    def newFile(self, newfile):
        global ROW_BUFFER
        ROW_BUFFER = []
        self.reader.end()
        self.reader = DataReader(parent=self, filename=newfile)
        self.reader.lineRead.connect(self.newLineRead)
        self.reader.start()     

    def onExit(self):
        global ROW_BUFFER
        if ROW_BUFFER:
            anglecolnum = getCol('Platen Motor Position')
            angle = round(float(ROW_BUFFER[0][anglecolnum]))
            newpt1 = processData(prevangle, radius1)
            newpt2 = processData(prevangle, radius2)
            ROW_BUFFER = []
            if (newpt1 != None and newpt2 != None):
                return [newpt1, newpt2]
            
    def end(self):
        self.reader.end()
        self.running = False

"""
class DataProcessor(QtCore.QObject):

    # initialize signal to deposition graph when a data point
    #   has been processed
    newData = QtCore.pyqtSignal(list)

    def __init__(self, parent=None, row=[]):
        super(DataProcessor, self).__init__()
        self.row = row

    def run(self):
        global ROW_BUFFER
        global changeZ
        while self.running:
            if ROW_BUFFER == []:
                ROW_BUFFER += [self.row]
                print 'first thing in row buffer'
            else:
                anglecolnum = getCol('Platen Motor Position')
                angle = round(float(self.row[anglecolnum]))
                zcolnum = getCol('Platen Zshift Motor 1 Position')
                zval = round(float(self.row[zcolnum]), 1)
                prevangle = round(float(ROW_BUFFER[-1][anglecolnum]), 0)
                prevz = round(float(ROW_BUFFER[-1][zcolnum]), 1)
                if (angle == prevangle and zval == prevz):
                    ROW_BUFFER += [self.row]
                    print 'adding to row buffer'
                elif (angle == prevangle):
                    # make new graph
                    print 'drawing new graph for z =', zval
                    newpt1 = sprocessData(prevz, prevangle, radius1)
                    newpt2 = processData(prevz, prevangle, radius2)
                    changeZ = True
                    ROW_BUFFER = [self.row]
                    if (newpt1 != None and newpt2 != None):
                        self.newData.emit([newpt1, newpt2])
                else:
                    print 'processing a set of points'
                    newpt1 = processData(zval, prevangle, radius1)
                    newpt2 = processData(zval, prevangle, radius2)
                    ROW_BUFFER = [self.row]
                    if (newpt1 != None and newpt2 != None):
                        self.newData.emit([newpt1, newpt2])

        
    # make sure to make one last call to processData when file finishes
"""
     

def roundZ(zcol):
    zrnd=np.round(zcol, decimals=zndec)
    for zval in zrnd:
        if zval not in filename_handler.FILE_INFO['Z_mm']:
            zval = -1
    return zrnd

def roundt(tcol):
    trnd=np.round(tcol, decimals=tndec)
    for tval in trnd:
        if tval not in filename_handler.FILE_INFO['TiltDeg']:
            tval = -1
    return trnd

def getRowRange():
    zcolnum = getCol('Platen Zshift Motor 1 Position')
    tcolnum = getCol('Src%d Motor Tilt Position' % int(filename_handler.FILE_INFO['Source']))
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
    



