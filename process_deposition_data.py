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

zndec = 2
tndec = 1
radius1 = 28.
radius2 = 45.

class ProcessorThread(QtCore.QThread):
    
    lineRead = QtCore.pyqtSignal(list)
    newData = QtCore.pyqtSignal(tuple)
    
    def __init__(self, parent=None, filename='default.csv'):
        super(ProcessorThread, self).__init__()
        self.file = filename
        self.rowBuffer = []
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
        if self.rowBuffer == []:
            self.rowBuffer += [row]
        else:
            anglecolnum = getCol('Platen Motor Position')
            angle = round(float(row[anglecolnum]))
            zcolnum = getCol('Platen Zshift Motor 1 Position')
            zval = round(float(row[zcolnum]), 1)
            prevangle = round(float(self.rowBuffer[-1][anglecolnum]), 0)
            prevz = round(float(self.rowBuffer[-1][zcolnum]), 1)
            if (angle == prevangle and zval == prevz):
                self.rowBuffer += [row]
            elif (angle == prevangle):
                # make new graph
                print 'drawing new graph for z =', zval
                self.processData(prevz, prevangle, radius1)
                self.processData(prevz, prevangle, radius2)
                self.changeZ = True
                self.rowBuffer = [row]
            else:
                self.processData(zval, prevangle, radius1)
                self.processData(zval, prevangle, radius2)
                self.rowBuffer = [row]

    def processData(self, z, angle, radius):
        global DEP_DATA
        rowRange = self.getRowRange()
        #print 't:', FILE_INFO.get('TiltDeg')
        #print 'rowRange:', rowRange
        if rowRange[1] - rowRange[0] <= 2:
            pass
        else:
            #print 'self.rowBuffer', self.rowBuffer
            dataArray = self.rowBuffer[rowRange[0]:(rowRange[1]+1)]
            dataArrayT = np.array(dataArray).T
            #print 'dataArrayT', dataArrayT
            timespan = self.getTimeSpan(dataArrayT)
            depRates = self.getDepRates(timespan, dataArrayT)
            rate0 = self.getXtalRate(3, dataArrayT).mean()
            rate = rate0
            if radius == radius1:
                if angle == 0 or self.changeZ:
                    #plot rate0 at (0, 0)
                    print 'plotting rate0 at (0,0)'
                    DEP_DATA.append((z, 0.0, 0.0, rate))
                    self.newData.emit((z, 0.0, 0.0, rate))
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
            self.newData.emit((z, x, y, rate))

    def roundZ(self, zcol):
        zrnd=np.round(zcol, decimals=zndec)
        for zval in zrnd:
            if zval not in FILE_INFO['Z_mm']:
                zval = -1
        return zrnd

    def roundt(self, tcol):
        trnd=np.round(tcol, decimals=tndec)
        for tval in trnd:
            if tval not in FILE_INFO['TiltDeg']:
                tval = -1
        return trnd

    def getRowRange(self):
        zcolnum = getCol('Platen Zshift Motor 1 Position')
        tcolnum = getCol('Src%d Motor Tilt Position' % int(FILE_INFO['Source']))
        data = np.array(self.rowBuffer)
        datacols = data.T
        zcol = map(float, datacols[zcolnum])
        tcol = map(float, datacols[tcolnum])
        inds_useful=np.where((self.roundZ(zcol)>=0)&
                                (self.roundt(tcol)>=0))[0]
        return (inds_useful[0], inds_useful[-1])

    def getTimeSpan(self, dataArrayT):
        datecol = getCol('Date')
        timecol = getCol('Time')
        datetimeTup = zip(dataArrayT[datecol], dataArrayT[timecol])
        startStr = datetimeTup[0][0] + ' ' + datetimeTup[0][1]
        endStr = datetimeTup[-1][0] + ' ' + datetimeTup[-1][1]
        durationObj = dateObjFloat(endStr) - dateObjFloat(startStr)
        return durationObj.total_seconds()

    def getXtalRate(self, ratenum, dataArrayT):
        rcolnum = getCol('Xtal%d Rate' % ratenum)
        return np.array(map(float, dataArrayT[rcolnum]))

    def getDepRates(self, timespan, dataArrayT):
        depRates = []
        for x in range(2,5):
            rateData = self.getXtalRate(x, dataArrayT)
            rateDiff = rateData[-1] - rateData[0]
            depRates += [rateDiff/timespan]
        return depRates

    def newFile(self, newfile):
        global DEP_DATA
        DEP_DATA = []
        self.rowBuffer = []
        self.reader.end()
        self.reader = DataReader(parent=self, filename=newfile)
        self.reader.lineRead.connect(self.newLineRead)
        self.reader.start()     

    # need to actually call this somewhere!
    def onExit(self):
        if self.rowBuffer:
            anglecolnum = getCol('Platen Motor Position')
            angle = round(float(self.rowBuffer[0][anglecolnum]))
            processData(prevangle, radius1)
            processData(prevangle, radius2)
            self.rowBuffer = []
            
    def end(self):
        self.reader.end()
        self.running = False
<<<<<<< HEAD

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
    



=======
>>>>>>> a5214829283867f6cb65566c52f98332055a2550
