# Allison Schubauer and Daisy Hernandez
# Created: 5/23/2013
# Last Updated: 5/30/2013
# For JCAP

import csv, time
from PyQt4 import QtCore

DATA_DICT = {}
DATA_HEADINGS = {}

""" thread that reads data from file """
class DataReader(QtCore.QThread):

    # initialize signal to graph when a full line has been read
    lineRead = QtCore.pyqtSignal(list)
    
    def __init__(self, parent=None, filename='default.csv'):
        super(DataReader, self).__init__()

        self.initData(filename)
        self.running = True

    def initData(self, filename):
        self.datafile = open(filename, 'rb')
        # read column headings and create lists to hold data
        headings = self.datafile.readline().split(',')
        # strip off '/r/n' at end of line - only works on Windows
        #headings[self.numColumns-1] = headings[self.numColumns-1][:-2]
        global DATA_DICT
        global DATA_HEADINGS
        # clear dictionary in case it has already been used for a different file
        DATA_DICT.clear()
        DATA_HEADINGS.clear()
        DATA_HEADINGS[0] = 'Time'
        DATA_DICT['Time'] = []
        DATA_HEADINGS[1] = 'Date'
        DATA_DICT['Date'] = []
        # initialize each heading with an array to store the column data
        for col in range(3, len(headings)):
            if headings[col] == '':
                break
            DATA_HEADINGS[col] = headings[col]
            DATA_DICT[headings[col]] = []
        self.numColumns = len(DATA_HEADINGS)
        self.lastEOFpos = self.datafile.tell()

    def run(self):
        global DATA_DICT
        global DATA_HEADINGS
        dataColNums = DATA_HEADINGS.keys()

        while self.running:
            self.datafile.seek(self.lastEOFpos)
            data = self.datafile.readline()
            row = data.split(',')
            strippedRow = []
            for col in (row[:2] + row[3:]):
                if col != '':
                    strippedRow += [col]
                else:
                    break
            if len(strippedRow) == self.numColumns and row[len(row)-1].endswith('\r\n'):
                # add the new info to the respective column
                for col in dataColNums:
                    heading = DATA_HEADINGS.get(col)
                    DATA_DICT[heading].append(row[col])
                # SEND SIGNAL
                self.lineRead.emit(strippedRow)
                # move the reader cursor only if we read in a full line
                self.lastEOFpos = self.datafile.tell()

        # close file after end() has been called
        self.datafile.close()

    def end(self):
        print "message received"
        self.running = False
        

