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
    lineRead = QtCore.pyqtSignal()
    
    def __init__(self, parent=None, filename='default.csv'):
        super(DataReader, self).__init__()

        self.initData(filename)
        self.running = True

    def initData(self, filename):
        self.datafile = open(filename, 'rb')
        # read column headings and create lists to hold data
        headings = self.datafile.readline().split(',')
        self.numColumns = len(headings)
        # strip off '/r/n' at end of line - only works on Windows
        headings[self.numColumns-1] = headings[self.numColumns-1][:-2]
        global DATA_DICT
        global DATA_HEADINGS
        # clear dictionary in case it has already been used for a different file
        DATA_DICT.clear()
        DATA_HEADINGS.clear()
        # initialize each heading with an array to store the column data
        for col in range(len(headings)):
            DATA_HEADINGS[col] = headings[col]
            DATA_DICT[headings[col]] = []
        self.lastEOFpos = self.datafile.tell()

    def run(self):
        global DATA_DICT
        global DATA_HEADINGS
        numColumns = len(DATA_DICT)

        while self.running:
            # control the reading speed
            time.sleep(0.001)
            self.datafile.seek(self.lastEOFpos)
            data = self.datafile.readline()
            row = data.split(',')
            if len(row) == numColumns and row[numColumns-1].endswith('\r\n'):
                # add the new info to the respective column
                for col in range(len(row)):
                    heading = DATA_HEADINGS.get(col)
                    DATA_DICT[heading].append(row[col])
                # SEND SIGNAL
                self.lineRead.emit()
                # move the reader cursor only if we read in a full line
                self.lastEOFpos = self.datafile.tell()

        # close file after end() has been called
        self.datafile.close()

    def end(self):
        print "message received"
        self.running = False
        

