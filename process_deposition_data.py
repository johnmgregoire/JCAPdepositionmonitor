# Allison Schubauer and Daisy Hernandez
# Created: 6/05/2013
# Last Updated: 6/12/2013
# For JCAP

import numpy as np
from PyQt4 import QtCore
from dictionary_helpers import *
import date_helpers
import filename_handler
import datareader

# global dictionary holds all processed (z, x, y, rate)
#   data for this experiment
DEP_DATA = []

zndec = 1
tndec = 0
radius1 = 28.
radius2 = 45.

""" does all of the data processing necessary for
    deposition plots """

class ProcessorThread(QtCore.QThread):

    # transfers new line from reader to MainMenu
    lineRead = QtCore.pyqtSignal(list)
    # transfers new processed data to deposition graph
    newData = QtCore.pyqtSignal(tuple)
    
    def __init__(self, parent=None, filename='default.csv'):
        super(ProcessorThread, self).__init__()
        self.file = filename
        self.rowBuffer = []
        self.changeZ = False
        self.running = True
        self.reader = datareader.DataReader(parent=self, filename=self.file)
        self.reader.lineRead.connect(self.newLineRead)

    def run(self):
        self.reader.start()
        while self.running:
            pass

    """ called whenever the reader sends a full line """
    def newLineRead(self, newRow):
        self.lineRead.emit(newRow)
        self.processRow(newRow)

    """ adds a new row to its own row buffer and processes the
        data in the row buffer if the azimuth or z-value of the
        instrument has changed """
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
                self.processData(prevz, prevangle, radius1)
                self.processData(prevz, prevangle, radius2)
                # indicates that center point will need to be
                #   computed in next round of processing
                self.changeZ = True
                # reset row buffer
                self.rowBuffer = [row]
            else:
                self.processData(zval, prevangle, radius1)
                self.processData(zval, prevangle, radius2)
                self.rowBuffer = [row]

    """ processes all rates at the same angle and z-value
        to produce a single (x, y, rate) data point """
    def processData(self, z, angle, radius):
        global DEP_DATA
        rowRange = self.getRowRange()
        # only one or two data points indicates a transitional
        #   angle that can be ignored
        if rowRange[1] - rowRange[0] <= 2:
            pass
        else:
            # get only valid rows from buffer
            dataArray = self.rowBuffer[rowRange[0]:(rowRange[1]+1)]
            # transpose matrix so that each column in the
            #   spreadsheet becomes a row
            dataArrayT = np.array(dataArray).T
            timespan = self.getTimeSpan(dataArrayT)
            depRates = self.getDepRates(timespan, dataArrayT)
            # normalize based on drifting center point
            rate0 = self.getXtalRate(3, dataArrayT).mean()
            rate = rate0
            if radius == radius1:
                if angle == 0 or self.changeZ:
                    # plot center point along with first set
                    #   of data for this z-value
                    DEP_DATA.append((z, 0.0, 0.0, rate))
                    self.newData.emit((z, 0.0, 0.0, rate))
                    self.changeZ = False
                x = radius * np.cos(angle * np.pi/180.)
                y = radius * np.sin(angle * np.pi/180.)
                # rate1 corresponds to Xtal4 Rate
                rate = rate0 * depRates[2]/depRates[1]
                print (angle, radius, z, x, y, rate)
            else:
                x = radius * np.cos(angle * np.pi/180. + np.pi)
                y = radius * np.sin(angle * np.pi/180. + np.pi)
                # rate2 corresponds to Xtal2 Rate
                rate = rate0 * depRates[0]/depRates[1]
            # store data points for initializing new graph
            DEP_DATA.append((z, x, y, rate))
            # indicate to exisiting graphs that there is
            #   new data to display
            self.newData.emit((z, x, y, rate))

    """ helper function to correct for instrument noise
        in measuring z-value """
    def roundZ(self, zcol):
        zrnd=np.round(zcol, decimals=zndec)
        for i, zval in enumerate(zrnd):
            if zval not in filename_handler.FILE_INFO['Z_mm']:
                zrnd[i] = -1
        return zrnd

    """ helper function to correct for instrument noise
        in measuring tilt """
    def roundt(self, tcol):
        trnd=np.round(tcol, decimals=tndec)
        for i, tval in enumerate(trnd):
            if tval not in filename_handler.FILE_INFO['TiltDeg']:
                trnd[i] = -1
        return trnd

    """ gets range of valid rows in row buffer based on
        whether z and t values match experimental parameters """
    def getRowRange(self):
        zcolnum = getCol('Platen Zshift Motor 1 Position')
        tcolnum = getCol('Src%d Motor Tilt Position' % int(filename_handler.FILE_INFO['Source']))
        data = np.array(self.rowBuffer)
        datacols = data.T
        zcol = map(float, datacols[zcolnum])
        tcol = map(float, datacols[tcolnum])
        inds_useful=np.where((self.roundZ(zcol)>=0)&
                                (self.roundt(tcol)>=0))[0]
        # if rowRange is nonzero, send it
        if inds_useful.size:
            return (inds_useful[0], inds_useful[-1])
        # otherwise, send dummy rowRange to processData
        return (0, 0)

    """ gets time span of valid data set for given angle
        and z-value """
    def getTimeSpan(self, dataArrayT):
        datecol = getCol('Date')
        timecol = getCol('Time')
        datetimeTup = zip(dataArrayT[datecol], dataArrayT[timecol])
        startStr = datetimeTup[0][0] + ' ' + datetimeTup[0][1]
        endStr = datetimeTup[-1][0] + ' ' + datetimeTup[-1][1]
        durationObj = date_helpers.dateObjFloat(endStr) - date_helpers.dateObjFloat(startStr)
        return durationObj.total_seconds()

    """ helper function to return column of Xtal rates
        from valid data set """
    def getXtalRate(self, ratenum, dataArrayT):
        rcolnum = getCol('Xtal%d Rate' % ratenum)
        return np.array(map(float, dataArrayT[rcolnum]))

    """ helper function to compute all deposition rates
        as time-averaged Xtal rates """
    def getDepRates(self, timespan, dataArrayT):
        depRates = []
        for x in range(2,5):
            rateData = self.getXtalRate(x, dataArrayT)
            rateDiff = rateData[-1] - rateData[0]
            depRates += [rateDiff/timespan]
        return depRates

    """ re-initializes data sets and reader when a new
        spreadsheet file is loaded """
    def newFile(self, newfile):
        global DEP_DATA
        DEP_DATA = []
        self.rowBuffer = []
        if self.reader:
            self.reader.end()
        self.reader = datareader.DataReader(parent=self, filename=newfile)
        self.reader.lineRead.connect(self.newLineRead)
        self.reader.start()

    """ empties row buffer and kills reader when experiment
        has ended """
    def onEndExperiment(self):
        if self.rowBuffer:
            anglecolnum = getCol('Platen Motor Position')
            angle = round(float(self.rowBuffer[0] [anglecolnum]))
            zcolnum = getCol('Platen Zshift Motor 1 Position')
            zval = round(float(self.rowBuffer[0][zcolnum]), 1)
            self.processData(zval, angle, radius1)
            self.processData(zval, angle, radius2)
            self.rowBuffer = []
        if self.reader:
            self.reader.end()
            self.reader = None

    """ kills both the reader and data processor threads;
        called when application exits """
    def end(self):
        if self.reader:
            self.reader.end()
        self.running = False
